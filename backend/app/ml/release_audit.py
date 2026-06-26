"""Release readiness checklist và audit trail offline cho CareerOS AI."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHECK_STATUSES = {"PASS", "WARNING", "FAIL"}
AUDIT_OUTCOMES = {"PASS", "WARNING", "FAIL"}
REQUIRED_CHECKS = {
    "dataset_version",
    "dataset_hash",
    "approved_labels",
    "benchmark_completed",
    "training_config",
    "experiment_record",
    "evaluation_report",
    "model_artifact",
    "review_pass",
    "candidate",
    "decision_record",
    "risk_accepted",
    "pytest",
    "compileall",
    "pip_check",
    "utf8",
    "mojibake",
    "pii_scan",
    "production_safe",
    "deployment_decision",
    "audit_completed",
}
REQUIRED_AUDIT_FIELDS = {
    "audit_id",
    "timestamp",
    "reviewer",
    "dataset_version",
    "model_version",
    "registry_version",
    "decision_id",
    "checklist_result",
    "notes",
    "passed",
    "production_change_allowed",
}
MOJIBAKE_PATTERN = re.compile(
    r"\u00c3|\u00c2|\u00e1\u00ba|\u00e1\u00bb|\u00c4|\u00c6|\u00c5|\ufffd|M\?|Kh\?|H\?\?|tr\?|\?\?\?"
)
EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_PATTERN = re.compile(r"(?<!\d)(?:\+?\d[\d\s().-]{8,}\d)(?!\d)")


def read_json(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError(f"File JSON phải là object: {path}")
    return payload


def write_json(path: str | Path, payload: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def stable_json(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def calculate_artifact_hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(stable_json(payload).encode("utf-8")).hexdigest()


def check(check_id: str, group: str, status: str, message: str) -> dict[str, str]:
    if status not in CHECK_STATUSES:
        raise ValueError(f"Checklist status không hợp lệ: {status}")
    return {"check_id": check_id, "group": group, "status": status, "message": message}


def validate_checklist(checklist: list[dict[str, Any]]) -> None:
    ids = [str(item.get("check_id") or "") for item in checklist]
    missing = sorted(REQUIRED_CHECKS - set(ids))
    duplicates = sorted(check_id for check_id in set(ids) if ids.count(check_id) > 1)
    if missing:
        raise ValueError(f"Checklist thiếu mục bắt buộc: {', '.join(missing)}.")
    if duplicates:
        raise ValueError(f"Checklist trùng mục: {', '.join(duplicates)}.")
    for item in checklist:
        if item.get("status") not in CHECK_STATUSES:
            raise ValueError(f"Checklist status không hợp lệ: {item.get('status')}.")


def summarize_checklist(checklist: list[dict[str, Any]]) -> dict[str, Any]:
    validate_checklist(checklist)
    counts = {
        status: sum(item["status"] == status for item in checklist)
        for status in ("PASS", "WARNING", "FAIL")
    }
    outcome = "FAIL" if counts["FAIL"] else ("WARNING" if counts["WARNING"] else "PASS")
    recommendation = {
        "PASS": "Release ready ở mức offline; chưa được phép thay đổi production.",
        "WARNING": "Chưa release ready hoàn toàn; cần xử lý warning trước deployment discussion.",
        "FAIL": "Không release ready; giữ baseline và khắc phục toàn bộ lỗi FAIL.",
    }[outcome]
    return {"outcome": outcome, "counts": counts, "recommendation": recommendation}


def validate_audit_record(
    record: dict[str, Any],
    *,
    require_reviewer: bool = True,
) -> None:
    missing = sorted(REQUIRED_AUDIT_FIELDS - record.keys())
    if missing:
        raise ValueError(f"Audit record thiếu field bắt buộc: {', '.join(missing)}.")
    if require_reviewer and not str(record.get("reviewer") or "").strip():
        raise ValueError("Write mode yêu cầu reviewer.")
    if record.get("production_change_allowed") is not False:
        raise ValueError("Phase 10.7 yêu cầu production_change_allowed=false.")
    checklist = record.get("checklist_result")
    if not isinstance(checklist, list):
        raise ValueError("checklist_result phải là list.")
    validate_checklist(checklist)
    summary = summarize_checklist(checklist)
    if record.get("passed") is not (summary["outcome"] == "PASS"):
        raise ValueError("passed không khớp checklist outcome.")


def build_release_audit(
    *,
    workspace: Path,
    manifest_path: Path,
    dataset_path: Path,
    training_config_path: Path,
    registry_path: Path,
    decision_path: Path | None,
    quality_evidence: dict[str, Any] | None,
    reviewer: str,
    audit_id: str,
    timestamp: str | None = None,
) -> dict[str, Any]:
    manifest = _read_optional_json(manifest_path)
    dataset = _read_optional_json(dataset_path)
    training_config = _read_optional_json(training_config_path)
    registry = _read_optional_json(registry_path)
    decision = _read_optional_json(decision_path) if decision_path else None
    artifact_paths = registry.get("artifact_paths", {}) if registry else {}
    if not isinstance(artifact_paths, dict):
        artifact_paths = {}
    experiment_path = _resolve_optional_path(workspace, artifact_paths.get("experiment"))
    evaluation_path = _resolve_optional_path(workspace, artifact_paths.get("evaluation_report"))
    model_path = _resolve_optional_path(workspace, artifact_paths.get("model"))
    model_metadata_path = _resolve_optional_path(workspace, artifact_paths.get("model_metadata"))
    experiment = _read_optional_json(experiment_path)
    evaluation = _read_optional_json(evaluation_path)
    model_metadata = _read_optional_json(model_metadata_path)

    checklist: list[dict[str, str]] = []
    dataset_version = str(manifest.get("dataset_version") or "") if manifest else ""
    checklist.append(
        check(
            "dataset_version",
            "Dataset",
            "PASS" if dataset_version else "FAIL",
            f"Dataset version: {dataset_version}" if dataset_version else "Manifest thiếu dataset_version.",
        )
    )
    expected_hash = str(manifest.get("artifact_hash") or "") if manifest else ""
    actual_hash = calculate_artifact_hash(dataset) if dataset else ""
    hash_ok = bool(expected_hash and actual_hash == expected_hash)
    checklist.append(
        check(
            "dataset_hash",
            "Dataset",
            "PASS" if hash_ok else "FAIL",
            "Dataset hash khớp manifest." if hash_ok else "Dataset hash thiếu hoặc không khớp manifest.",
        )
    )
    beta_count = int(manifest.get("beta_count", 0)) if manifest else 0
    approved_beta = _approved_beta_labels(dataset)
    if beta_count == 0:
        label_status = "WARNING"
        label_message = "Dataset chưa có approved beta labels; hiện chỉ dùng synthetic/benchmark."
    elif approved_beta == beta_count:
        label_status = "PASS"
        label_message = f"Đã xác nhận {approved_beta} approved beta labels."
    else:
        label_status = "FAIL"
        label_message = f"Approved beta labels không khớp manifest: {approved_beta}/{beta_count}."
    checklist.append(check("approved_labels", "Dataset", label_status, label_message))
    benchmark_ok = bool(evaluation and evaluation.get("benchmark_results"))
    checklist.append(
        check(
            "benchmark_completed",
            "Dataset",
            "PASS" if benchmark_ok else "FAIL",
            "Evaluation có benchmark results." if benchmark_ok else "Chưa có benchmark results trong evaluation.",
        )
    )

    checklist.append(
        check(
            "training_config",
            "Training",
            "PASS" if training_config else "FAIL",
            "Training config tồn tại." if training_config else "Thiếu training config.",
        )
    )
    checklist.append(
        check(
            "experiment_record",
            "Training",
            "PASS" if experiment else "FAIL",
            "Experiment record tồn tại." if experiment else "Thiếu experiment record.",
        )
    )
    checklist.append(
        check(
            "evaluation_report",
            "Training",
            "PASS" if evaluation else "FAIL",
            "Evaluation report tồn tại." if evaluation else "Thiếu evaluation report.",
        )
    )
    model_ok = bool(model_path and model_path.exists() and model_metadata)
    checklist.append(
        check(
            "model_artifact",
            "Training",
            "PASS" if model_ok else "FAIL",
            "Model artifact và metadata tồn tại." if model_ok else "Thiếu model artifact hoặc model metadata.",
        )
    )

    review_outcome = _latest_review_outcome(registry)
    checklist.append(
        check(
            "review_pass",
            "Model Review",
            "PASS" if review_outcome == "PASS" else "FAIL",
            f"Review outcome: {review_outcome or 'chưa có'}",
        )
    )
    candidate_ok = bool(registry and registry.get("status") == "candidate")
    checklist.append(
        check(
            "candidate",
            "Model Review",
            "PASS" if candidate_ok else "FAIL",
            "Registry có status=candidate." if candidate_ok else "Chưa có registry candidate.",
        )
    )
    decision_ok = bool(
        decision
        and decision.get("candidate_model_version") == (registry or {}).get("model_version")
        and decision.get("production_change_allowed") is False
    )
    checklist.append(
        check(
            "decision_record",
            "Model Review",
            "PASS" if decision_ok else "FAIL",
            "Decision record hợp lệ và khớp candidate." if decision_ok else "Thiếu hoặc lệch decision record.",
        )
    )
    risk = str((decision or {}).get("risk_level") or "")
    risk_ok = risk in {"low", "medium"} and (decision or {}).get("decision") != "reject_candidate"
    checklist.append(
        check(
            "risk_accepted",
            "Model Review",
            "PASS" if risk_ok else ("WARNING" if risk == "high" else "FAIL"),
            f"Risk level: {risk or 'chưa có'}",
        )
    )

    evidence = quality_evidence or {}
    for check_id, label in (
        ("pytest", "pytest"),
        ("compileall", "compileall"),
        ("pip_check", "pip check"),
    ):
        value = evidence.get(check_id)
        status = "PASS" if value is True else ("FAIL" if value is False else "WARNING")
        message = f"{label}: {'pass' if value is True else 'fail' if value is False else 'chưa có evidence'}."
        checklist.append(check(check_id, "Quality", status, message))

    scan_paths = [
        path
        for path in (
            manifest_path,
            dataset_path,
            training_config_path,
            registry_path if registry_path.exists() else None,
            decision_path,
            experiment_path,
            evaluation_path,
            model_metadata_path,
        )
        if path is not None and path.exists()
    ]
    utf8_ok, mojibake_ok = _scan_text_files(scan_paths)
    checklist.append(
        check("utf8", "Quality", "PASS" if utf8_ok else "FAIL", "UTF-8 hợp lệ." if utf8_ok else "Có file không phải UTF-8 hoặc có BOM.")
    )
    checklist.append(
        check("mojibake", "Quality", "PASS" if mojibake_ok else "FAIL", "Không phát hiện mojibake." if mojibake_ok else "Phát hiện mojibake.")
    )
    pii_ok = _dataset_pii_safe(dataset)
    checklist.append(
        check("pii_scan", "Quality", "PASS" if pii_ok else "FAIL", "Không phát hiện PII." if pii_ok else "Phát hiện PII trong dataset.")
    )

    production_safe_ok = bool(
        registry
        and registry.get("production_safe") is False
        and (decision is None or decision.get("production_change_allowed") is False)
    )
    checklist.append(
        check(
            "production_safe",
            "Governance",
            "PASS" if production_safe_ok else "FAIL",
            "Production boundary được giữ." if production_safe_ok else "Production safety metadata thiếu hoặc không hợp lệ.",
        )
    )
    checklist.append(
        check(
            "deployment_decision",
            "Governance",
            "PASS" if decision_ok else "FAIL",
            "Deployment decision đã được ghi." if decision_ok else "Chưa có deployment decision hợp lệ.",
        )
    )
    checklist.append(check("audit_completed", "Governance", "PASS", "Checklist đã được audit đầy đủ."))

    summary = summarize_checklist(checklist)
    record = {
        "audit_id": audit_id,
        "timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
        "reviewer": reviewer,
        "dataset_version": dataset_version or None,
        "model_version": (registry or {}).get("model_version"),
        "registry_version": registry_path.stem if registry else None,
        "decision_id": (decision or {}).get("decision_id"),
        "checklist_result": checklist,
        "checklist_summary": summary,
        "notes": "Release readiness offline; không cho phép thay đổi production.",
        "passed": summary["outcome"] == "PASS",
        "production_change_allowed": False,
    }
    validate_audit_record(record, require_reviewer=bool(reviewer))
    return record


def _read_optional_json(path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.exists():
        return None
    return read_json(path)


def _resolve_optional_path(workspace: Path, value: Any) -> Path | None:
    if not value:
        return None
    path = Path(str(value))
    return path if path.is_absolute() else workspace / path


def _latest_review_outcome(registry: dict[str, Any] | None) -> str | None:
    history = (registry or {}).get("review_history")
    if isinstance(history, list) and history:
        return str(history[-1].get("outcome") or "") or None
    return None


def _approved_beta_labels(dataset: dict[str, Any] | None) -> int:
    cases = (dataset or {}).get("cases")
    if not isinstance(cases, list):
        return 0
    count = 0
    for case in cases:
        if not isinstance(case, dict) or case.get("source") != "beta":
            continue
        if case.get("approved_for_training") is True and case.get("anonymized") is True:
            count += 1
    return count


def _scan_text_files(paths: list[Path]) -> tuple[bool, bool]:
    utf8_ok = True
    mojibake_ok = True
    for path in paths:
        data = path.read_bytes()
        if data.startswith(b"\xef\xbb\xbf"):
            utf8_ok = False
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            utf8_ok = False
            continue
        if MOJIBAKE_PATTERN.search(text):
            mojibake_ok = False
    return utf8_ok, mojibake_ok


def _dataset_pii_safe(dataset: dict[str, Any] | None) -> bool:
    cases = (dataset or {}).get("cases")
    if not isinstance(cases, list):
        return False
    for case in cases:
        if not isinstance(case, dict):
            return False
        scan_payload = {key: value for key, value in case.items() if key != "content_hash"}
        text = json.dumps(scan_payload, ensure_ascii=False)
        if EMAIL_PATTERN.search(text) or PHONE_PATTERN.search(text):
            return False
    return True
