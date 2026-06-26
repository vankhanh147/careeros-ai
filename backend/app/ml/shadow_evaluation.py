"""Contract và safety validator cho Shadow Evaluation planning.

Module không chạy inference, không thay production score và không tạo output
user-facing. Mọi plan trong Phase 11.0 đều giữ runtime_activation_allowed=false.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ALLOWED_MODES = {"disabled", "dry_run", "shadow"}
REQUIRED_CONFIG_FIELDS = {
    "enabled",
    "candidate_model_version",
    "candidate_registry_path",
    "mode",
    "sample_rate",
    "max_latency_ms",
    "log_disagreements_only",
    "store_raw_text",
    "production_score_source",
    "allow_user_facing_output",
}


def read_json(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError(f"File JSON phải là object: {path}")
    return payload


def write_json(path: str | Path, payload: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_shadow_config(path: str | Path) -> dict[str, Any]:
    config = read_json(path)
    validate_shadow_config(config)
    return config


def validate_shadow_config(config: dict[str, Any]) -> None:
    missing = sorted(REQUIRED_CONFIG_FIELDS - config.keys())
    if missing:
        raise ValueError(f"Shadow config thiếu field bắt buộc: {', '.join(missing)}.")
    for field in ("enabled", "log_disagreements_only", "store_raw_text", "allow_user_facing_output"):
        if not isinstance(config[field], bool):
            raise ValueError(f"{field} phải là boolean.")
    if config["mode"] not in ALLOWED_MODES:
        raise ValueError("mode phải là disabled, dry_run hoặc shadow.")
    sample_rate = config["sample_rate"]
    if not isinstance(sample_rate, (int, float)) or not 0 <= float(sample_rate) <= 1:
        raise ValueError("sample_rate phải nằm trong khoảng 0..1.")
    max_latency = config["max_latency_ms"]
    if not isinstance(max_latency, int) or isinstance(max_latency, bool) or max_latency <= 0:
        raise ValueError("max_latency_ms phải là số nguyên dương.")
    if config["allow_user_facing_output"] is not False:
        raise ValueError("allow_user_facing_output bắt buộc phải false.")
    if config["store_raw_text"] is not False:
        raise ValueError("store_raw_text bắt buộc phải false.")
    if config["production_score_source"] != "rule_based":
        raise ValueError("production_score_source bắt buộc là rule_based.")


def resolve_workspace_path(workspace: Path, value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else workspace / path


def create_shadow_plan(
    *,
    config: dict[str, Any],
    workspace: Path,
    generated_at: str | None = None,
) -> dict[str, Any]:
    validate_shadow_config(config)
    safety_checks = [
        _check("USER_FACING_BLOCKED", True, "Không cho phép output ML hiển thị cho user."),
        _check("RAW_TEXT_BLOCKED", True, "Không lưu raw CV/JD text."),
        _check("RULE_BASED_SOURCE", True, "Production score tiếp tục lấy từ rule-based matcher."),
        _check("RUNTIME_DISABLED", True, "Phase 11.0 không cho phép runtime shadow inference."),
    ]
    requested_mode = str(config["mode"])
    requested_enabled = bool(config["enabled"])
    candidate_status = "not_checked"
    warnings: list[str] = []
    registry_path: Path | None = None
    registry: dict[str, Any] | None = None

    if not requested_enabled or requested_mode == "disabled":
        effective_mode = "disabled"
        recommendation = "Giữ shadow disabled. Chỉ bật planning khi có candidate đã review."
        if requested_enabled != (requested_mode != "disabled"):
            warnings.append("enabled và mode chưa đồng nhất; plan được hạ về disabled.")
    elif requested_mode == "dry_run":
        effective_mode = "dry_run"
        recommendation = "Có thể đánh giá config/candidate offline; không chạy inference."
    else:
        raw_registry_path = str(config.get("candidate_registry_path") or "").strip()
        if not raw_registry_path:
            candidate_status = "missing"
            effective_mode = "disabled"
            warnings.append("mode=shadow nhưng thiếu candidate_registry_path.")
            recommendation = "Giữ shadow disabled cho tới khi có candidate registry hợp lệ."
        else:
            registry_path = resolve_workspace_path(workspace, raw_registry_path)
            if not registry_path.exists():
                candidate_status = "not_found"
                effective_mode = "disabled"
                warnings.append("Không tìm thấy candidate registry.")
                recommendation = "Giữ shadow disabled và hoàn tất training/review candidate."
            else:
                try:
                    registry = read_json(registry_path)
                except (OSError, ValueError, json.JSONDecodeError):
                    candidate_status = "invalid"
                    effective_mode = "disabled"
                    warnings.append("Candidate registry không đọc được.")
                    recommendation = "Giữ shadow disabled và sửa registry metadata."
                else:
                    candidate_status = str(registry.get("status") or "unknown")
                    expected_version = str(config.get("candidate_model_version") or "").strip()
                    version_matches = bool(
                        expected_version and registry.get("model_version") == expected_version
                    )
                    safe_candidate = (
                        candidate_status == "candidate"
                        and registry.get("production_safe") is False
                        and version_matches
                    )
                    if safe_candidate:
                        effective_mode = "shadow"
                        recommendation = (
                            "Candidate đủ điều kiện tạo shadow plan nội bộ; "
                            "runtime vẫn bị khóa trong Phase 11.0."
                        )
                    else:
                        effective_mode = "disabled"
                        warnings.append(
                            "Registry phải có status=candidate, production_safe=false "
                            "và model_version khớp config."
                        )
                        recommendation = "Giữ shadow disabled cho tới khi candidate vượt safety gate."

    outcome = "WARNING" if warnings else "PASS"
    if effective_mode == "disabled" and requested_mode == "shadow":
        outcome = "WARNING"
    return {
        "plan_version": "shadow_evaluation_plan_v1",
        "generated_at": generated_at or datetime.now(timezone.utc).isoformat(),
        "requested_enabled": requested_enabled,
        "requested_mode": requested_mode,
        "effective_enabled": False,
        "effective_mode": effective_mode,
        "candidate_model_version": config.get("candidate_model_version") or None,
        "candidate_registry_path": str(registry_path) if registry_path else str(config.get("candidate_registry_path") or ""),
        "candidate_status": candidate_status,
        "sample_rate": float(config["sample_rate"]),
        "max_latency_ms": int(config["max_latency_ms"]),
        "log_disagreements_only": bool(config["log_disagreements_only"]),
        "store_raw_text": False,
        "production_score_source": "rule_based",
        "allow_user_facing_output": False,
        "runtime_activation_allowed": False,
        "safety_checks": safety_checks,
        "warnings": warnings,
        "outcome": outcome,
        "recommendation": recommendation,
    }


def _check(check_id: str, passed: bool, message: str) -> dict[str, Any]:
    return {
        "check_id": check_id,
        "status": "PASS" if passed else "FAIL",
        "message": message,
    }
