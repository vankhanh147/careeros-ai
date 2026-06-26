"""Review gate cho model registry offline của CareerOS AI.

Module chỉ kiểm tra metadata và artifacts của training job. Module không train,
không inference, không thay production scoring và không promote production.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REVIEW_LEVELS = {"PASS", "WARNING", "FAIL"}
REVIEWABLE_STATUSES = {"draft", "under_review", "candidate", "rejected"}
REQUIRED_CONFIG_FIELDS = {
    "registry_path",
    "dataset_manifest_path",
    "minimum_accuracy",
    "minimum_macro_f1",
    "warning_margin",
    "benchmark_required",
    "required_evaluation_fields",
}
REQUIRED_REGISTRY_FIELDS = {
    "model_name",
    "model_version",
    "dataset_version",
    "dataset_hash",
    "feature_version",
    "accuracy",
    "macro_f1",
    "artifact_paths",
    "status",
    "production_safe",
}
REQUIRED_ARTIFACT_KEYS = {
    "model",
    "vectorizer",
    "labels",
    "model_metadata",
    "experiment",
    "evaluation_report",
}


@dataclass(frozen=True)
class ReviewIssue:
    level: str
    code: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"level": self.level, "code": self.code, "message": self.message}


def read_json(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError(f"File JSON phải là object: {path}")
    return payload


def write_json(path: str | Path, payload: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_model_review_config(path: str | Path) -> dict[str, Any]:
    config = read_json(path)
    missing = sorted(REQUIRED_CONFIG_FIELDS - config.keys())
    if missing:
        raise ValueError(f"model review config thiếu field bắt buộc: {', '.join(missing)}")
    for field in ("minimum_accuracy", "minimum_macro_f1", "warning_margin"):
        value = config[field]
        if not isinstance(value, (int, float)) or not 0 <= float(value) <= 1:
            raise ValueError(f"{field} phải nằm trong khoảng 0..1.")
    if not isinstance(config["benchmark_required"], bool):
        raise ValueError("benchmark_required phải là boolean.")
    if not isinstance(config["required_evaluation_fields"], list):
        raise ValueError("required_evaluation_fields phải là list.")
    return config


def resolve_workspace_path(workspace: Path, value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else workspace / path


def calculate_file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _add(issues: list[ReviewIssue], level: str, code: str, message: str) -> None:
    issues.append(ReviewIssue(level, code, message))


def _validate_score(
    issues: list[ReviewIssue],
    *,
    value: Any,
    field: str,
    threshold: float,
    warning_margin: float,
) -> None:
    if not isinstance(value, (int, float)) or not 0 <= float(value) <= 1:
        _add(issues, "FAIL", f"INVALID_{field.upper()}", f"{field} phải nằm trong khoảng 0..1.")
        return
    score = float(value)
    if score < threshold:
        level = "WARNING" if score >= max(0.0, threshold - warning_margin) else "FAIL"
        _add(
            issues,
            level,
            f"LOW_{field.upper()}",
            f"{field}={score:.3f}, ngưỡng yêu cầu={threshold:.3f}.",
        )


def review_registry(
    *,
    registry_path: Path,
    config: dict[str, Any],
    workspace: Path,
    registry_dir: Path | None = None,
) -> dict[str, Any]:
    issues: list[ReviewIssue] = []
    reviewed_at = datetime.now(timezone.utc).isoformat()
    if not registry_path.exists():
        _add(issues, "FAIL", "REGISTRY_NOT_FOUND", f"Không tìm thấy registry: {registry_path}")
        return _build_result(registry_path, None, issues, reviewed_at)

    try:
        registry = read_json(registry_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        _add(issues, "FAIL", "REGISTRY_INVALID", f"Không đọc được registry: {exc}")
        return _build_result(registry_path, None, issues, reviewed_at)

    missing_fields = sorted(REQUIRED_REGISTRY_FIELDS - registry.keys())
    if missing_fields:
        _add(
            issues,
            "FAIL",
            "REGISTRY_FIELDS_MISSING",
            f"Registry thiếu field: {', '.join(missing_fields)}.",
        )

    status = str(registry.get("status") or "")
    if status not in REVIEWABLE_STATUSES:
        _add(issues, "FAIL", "INVALID_REGISTRY_STATUS", f"Registry status không hợp lệ: {status or '(rỗng)'}.")
    if registry.get("production_safe") is not False:
        _add(issues, "FAIL", "PRODUCTION_BOUNDARY", "Review gate yêu cầu production_safe=false.")
    if not str(registry.get("feature_version") or "").strip():
        _add(issues, "FAIL", "FEATURE_VERSION_MISSING", "feature_version không được rỗng.")

    manifest_path = resolve_workspace_path(workspace, str(config["dataset_manifest_path"]))
    if not manifest_path.exists():
        _add(issues, "FAIL", "MANIFEST_NOT_FOUND", f"Không tìm thấy dataset manifest: {manifest_path}")
        manifest: dict[str, Any] = {}
    else:
        try:
            manifest = read_json(manifest_path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            manifest = {}
            _add(issues, "FAIL", "MANIFEST_INVALID", f"Không đọc được dataset manifest: {exc}")

    if manifest:
        if registry.get("dataset_version") != manifest.get("dataset_version"):
            _add(issues, "FAIL", "DATASET_VERSION_MISMATCH", "dataset_version không khớp manifest.")
        if registry.get("dataset_hash") != manifest.get("artifact_hash"):
            _add(issues, "FAIL", "DATASET_HASH_MISMATCH", "dataset_hash không khớp artifact_hash trong manifest.")

    artifact_paths = registry.get("artifact_paths")
    if not isinstance(artifact_paths, dict):
        _add(issues, "FAIL", "ARTIFACT_PATHS_INVALID", "artifact_paths phải là JSON object từ Training Job Contract.")
        artifact_paths = {}
    missing_artifact_keys = sorted(REQUIRED_ARTIFACT_KEYS - artifact_paths.keys())
    if missing_artifact_keys:
        _add(
            issues,
            "FAIL",
            "ARTIFACT_KEYS_MISSING",
            f"artifact_paths thiếu key: {', '.join(missing_artifact_keys)}.",
        )

    resolved_artifacts: dict[str, Path] = {}
    for key in REQUIRED_ARTIFACT_KEYS:
        raw_path = artifact_paths.get(key)
        if not raw_path:
            continue
        path = resolve_workspace_path(workspace, str(raw_path))
        resolved_artifacts[key] = path
        if not path.exists():
            _add(issues, "FAIL", f"{key.upper()}_NOT_FOUND", f"Không tìm thấy {key}: {path}")

    experiment = _load_linked_json(resolved_artifacts.get("experiment"), "EXPERIMENT", issues)
    evaluation = _load_linked_json(resolved_artifacts.get("evaluation_report"), "EVALUATION", issues)
    if experiment:
        if experiment.get("model_version") != registry.get("model_version"):
            _add(issues, "FAIL", "EXPERIMENT_MODEL_MISMATCH", "Experiment record không khớp model_version.")
        if experiment.get("dataset_hash") != registry.get("dataset_hash"):
            _add(issues, "FAIL", "EXPERIMENT_HASH_MISMATCH", "Experiment record không khớp dataset_hash.")
    if evaluation:
        if evaluation.get("model_version") != registry.get("model_version"):
            _add(issues, "FAIL", "EVALUATION_MODEL_MISMATCH", "Evaluation report không khớp model_version.")
        metrics = evaluation.get("metrics")
        if not isinstance(metrics, dict):
            _add(issues, "FAIL", "EVALUATION_METRICS_MISSING", "Evaluation report thiếu metrics.")
        else:
            for field in config["required_evaluation_fields"]:
                if field not in metrics:
                    _add(issues, "FAIL", "EVALUATION_FIELD_MISSING", f"Evaluation metrics thiếu field: {field}.")
        if config["benchmark_required"] and not evaluation.get("benchmark_results"):
            _add(
                issues,
                "FAIL",
                "BENCHMARK_REQUIRED",
                "Config yêu cầu benchmark_results nhưng evaluation report chưa có.",
            )

    _validate_score(
        issues,
        value=registry.get("accuracy"),
        field="accuracy",
        threshold=float(config["minimum_accuracy"]),
        warning_margin=float(config["warning_margin"]),
    )
    _validate_score(
        issues,
        value=registry.get("macro_f1"),
        field="macro_f1",
        threshold=float(config["minimum_macro_f1"]),
        warning_margin=float(config["warning_margin"]),
    )

    registry_scan_dir = registry_dir or registry_path.parent
    duplicates = []
    model_version = str(registry.get("model_version") or "")
    if model_version and registry_scan_dir.exists():
        for candidate in registry_scan_dir.glob("*.json"):
            try:
                payload = read_json(candidate)
            except (OSError, ValueError, json.JSONDecodeError):
                continue
            if payload.get("model_version") == model_version and candidate.resolve() != registry_path.resolve():
                duplicates.append(str(candidate))
    if duplicates:
        _add(
            issues,
            "FAIL",
            "DUPLICATE_REGISTRY",
            f"model_version xuất hiện trong nhiều registry: {', '.join(sorted(duplicates))}.",
        )

    return _build_result(registry_path, registry, issues, reviewed_at)


def _load_linked_json(
    path: Path | None,
    label: str,
    issues: list[ReviewIssue],
) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    try:
        return read_json(path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        _add(issues, "FAIL", f"{label}_INVALID", f"Không đọc được {label.lower()}: {exc}")
        return {}


def _build_result(
    registry_path: Path,
    registry: dict[str, Any] | None,
    issues: list[ReviewIssue],
    reviewed_at: str,
) -> dict[str, Any]:
    fail_count = sum(issue.level == "FAIL" for issue in issues)
    warning_count = sum(issue.level == "WARNING" for issue in issues)
    outcome = "FAIL" if fail_count else ("WARNING" if warning_count else "PASS")
    target_status = "rejected" if outcome == "FAIL" else "candidate"
    recommendation = (
        "Không promote. Khắc phục toàn bộ lỗi FAIL rồi review lại."
        if outcome == "FAIL"
        else (
            "Có thể chuyển candidate, nhưng cần xem xét các WARNING trước deployment decision."
            if outcome == "WARNING"
            else "Đủ điều kiện chuyển candidate; vẫn chưa được phép trở thành production."
        )
    )
    return {
        "registry_path": str(registry_path),
        "model_version": registry.get("model_version") if registry else None,
        "reviewed_at": reviewed_at,
        "outcome": outcome,
        "target_status": target_status,
        "production_safe": False,
        "issues": [issue.as_dict() for issue in issues],
        "summary": {
            "pass": 1 if outcome == "PASS" else 0,
            "warnings": warning_count,
            "failures": fail_count,
        },
        "recommendation": recommendation,
    }


def apply_review_result(registry_path: Path, result: dict[str, Any]) -> dict[str, Any]:
    if result["outcome"] not in REVIEW_LEVELS:
        raise ValueError("Review outcome không hợp lệ.")
    registry = read_json(registry_path)
    if registry.get("production_safe") is not False:
        raise ValueError("Không thể cập nhật registry có production_safe khác false.")
    target_status = str(result["target_status"])
    if target_status not in {"candidate", "rejected"}:
        raise ValueError("Review gate chỉ được cập nhật candidate hoặc rejected.")
    history = registry.get("review_history", [])
    if not isinstance(history, list):
        history = []
    history.append(
        {
            "reviewed_at": result["reviewed_at"],
            "outcome": result["outcome"],
            "status": target_status,
            "issues": result["issues"],
            "recommendation": result["recommendation"],
        }
    )
    registry["status"] = target_status
    registry["production_safe"] = False
    registry["review_history"] = history
    write_json(registry_path, registry)
    return registry
