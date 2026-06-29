"""Dataset Promotion Planning Bridge.

Bridge chỉ revalidate QA evidence và lập kế hoạch. Không sửa input, không tạo
dataset metadata, không promote dataset và không train model.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

from app.ml.training_infra import validate_label_review_cases


DATASET_VERSION_PATTERN = re.compile(r"^dataset_v(\d+)$")
MOJIBAKE_PATTERN = re.compile(
    r"\u00c3|\u00c2|\u00e1\u00ba|\u00e1\u00bb|\u00c4|\u00c6|\u00c5|\ufffd|M\?|Kh\?|H\?\?|tr\?|\?\?\?"
)
EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_PATTERN = re.compile(r"(?<!\d)(?:\+?\d[\d\s().-]{8,}\d)(?!\d)")
ISO_TIMESTAMP_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:\+00:00|Z)?")


def read_json(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError(f"File JSON phải là object: {path}")
    return payload


def write_json(path: str | Path, payload: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_no_qa_plan(*, source_qa_report: str) -> dict[str, Any]:
    return {
        "status": "no_qa_report",
        "source_qa_report": source_qa_report,
        "source_draft": None,
        "source_export_id": None,
        "current_dataset_version": None,
        "target_dataset_version": None,
        "total_cases": 0,
        "promotion_ready": 0,
        "blocked_cases": 0,
        "blockers": ["NO_QA_REPORT"],
        "estimated_dataset_size": None,
        "recommendation": "run Label Review Draft QA Bridge write mode first",
        "promotion_allowed": False,
        "promotion_executed": False,
        "training_allowed": False,
        "input_modified": False,
    }


def build_dataset_promotion_plan(
    *,
    qa_report: Mapping[str, Any],
    draft: Mapping[str, Any],
    manifest: Mapping[str, Any],
    source_qa_report: str,
    source_draft: str,
    existing_plan: Mapping[str, Any] | None = None,
    utf8_valid: bool = True,
    bom_free: bool = True,
) -> dict[str, Any]:
    cases_value = draft.get("cases")
    if not isinstance(cases_value, list):
        raise ValueError("Label Review Draft thiếu cases dạng list.")
    cases = [dict(case) for case in cases_value if isinstance(case, Mapping)]
    if len(cases) != len(cases_value):
        raise ValueError("Label Review Draft case phải là JSON object.")
    _reject_duplicates(draft, cases)

    current_version = str(manifest.get("dataset_version") or "")
    target_version = next_dataset_version(current_version)
    current_size = manifest.get("total_cases")
    if not isinstance(current_size, int) or current_size < 0:
        raise ValueError("Manifest total_cases không hợp lệ.")

    fresh_validation = validate_label_review_cases(cases)
    blockers: list[str] = []
    qa_errors = _non_negative_int(qa_report.get("errors_count"), "QA errors_count")
    qa_ready_count = _non_negative_int(
        qa_report.get("ready_for_promotion_count"), "QA ready_for_promotion_count"
    )
    qa_blockers = qa_report.get("promotion_blockers")
    if not isinstance(qa_blockers, list):
        raise ValueError("QA promotion_blockers phải là list.")
    if qa_errors > 0:
        blockers.append("QA_VALIDATION_ERRORS")
    if qa_blockers:
        blockers.extend(f"QA:{str(item)}" for item in qa_blockers)
    if qa_ready_count == 0 or qa_report.get("ready_for_promotion") is not True:
        blockers.append("NO_QA_PROMOTION_READY_CASES")

    fresh_errors = int(fresh_validation["errors_count"])
    fresh_ready_count = int(fresh_validation["ready_for_promotion_count"])
    if fresh_errors > 0:
        blockers.append("DRAFT_VALIDATION_ERRORS")
    if fresh_ready_count == 0:
        blockers.append("NO_DRAFT_PROMOTION_READY_CASES")
    if qa_ready_count != fresh_ready_count or qa_errors != fresh_errors:
        blockers.append("STALE_QA_REPORT")

    blockers.extend(validate_case_readiness(cases))
    if not utf8_valid:
        blockers.append("INVALID_UTF8")
    if not bom_free:
        blockers.append("UTF8_BOM_FOUND")
    serialized = json.dumps({"qa": qa_report, "draft": draft}, ensure_ascii=False)
    if MOJIBAKE_PATTERN.search(serialized):
        blockers.append("MOJIBAKE_FOUND")
    pii_text = ISO_TIMESTAMP_PATTERN.sub("", serialized)
    if EMAIL_PATTERN.search(pii_text) or PHONE_PATTERN.search(pii_text):
        blockers.append("PII_FOUND")

    source_export_id = str(draft.get("export_id") or "").strip()
    if not source_export_id:
        blockers.append("MISSING_EXPORT_ID")
    if existing_plan and existing_plan.get("source_export_id") == source_export_id:
        blockers.append("DUPLICATE_EXPORT_PLAN")

    blockers = list(dict.fromkeys(blockers))
    total_cases = len(cases)
    promotion_ready = fresh_ready_count
    blocked_cases = max(0, total_cases - promotion_ready)
    promotion_allowed = (
        not blockers
        and qa_errors == 0
        and fresh_errors == 0
        and promotion_ready > 0
        and DATASET_VERSION_PATTERN.fullmatch(target_version) is not None
    )
    return {
        "status": "promotion_plan_ready" if promotion_allowed else "blocked",
        "source_qa_report": source_qa_report,
        "source_draft": source_draft,
        "source_export_id": source_export_id or None,
        "current_dataset_version": current_version,
        "target_dataset_version": target_version,
        "total_cases": total_cases,
        "promotion_ready": promotion_ready,
        "blocked_cases": blocked_cases,
        "blockers": blockers,
        "estimated_dataset_size": current_size + promotion_ready,
        "qa_snapshot": {
            "errors_count": qa_errors,
            "warnings_count": qa_report.get("warnings_count", 0),
            "ready_for_promotion_count": qa_ready_count,
        },
        "recommendation": (
            "Có thể lập Dataset Promotion dry-run; bridge không tự động promote."
            if promotion_allowed
            else "keep current dataset"
        ),
        "promotion_allowed": promotion_allowed,
        "promotion_executed": False,
        "training_allowed": False,
        "input_modified": False,
    }


def validate_case_readiness(cases: list[dict[str, Any]]) -> list[str]:
    blockers: list[str] = []
    dataset_versions = {
        str(case.get("dataset_version") or "").strip()
        for case in cases
        if str(case.get("dataset_version") or "").strip()
    }
    if len(dataset_versions) != 1:
        blockers.append("INCONSISTENT_CASE_DATASET_VERSION")
    for case in cases:
        case_id = str(case.get("case_id") or "unknown")
        status = str(case.get("review_status") or "")
        if status not in {"APPROVED", "PROMOTED", "TRAINABLE"}:
            blockers.append(f"{case_id}:INVALID_REVIEW_STATUS")
        if case.get("approved_for_training") is not True:
            blockers.append(f"{case_id}:TRAINING_NOT_APPROVED")
        if case.get("anonymized") is not True:
            blockers.append(f"{case_id}:NOT_ANONYMIZED")
        if not str(case.get("reviewer") or "").strip():
            blockers.append(f"{case_id}:MISSING_REVIEWER")
        confidence = case.get("label_confidence")
        if (
            not isinstance(confidence, (int, float))
            or isinstance(confidence, bool)
            or not 0 <= float(confidence) <= 1
        ):
            blockers.append(f"{case_id}:INVALID_LABEL_CONFIDENCE")
    return blockers


def next_dataset_version(current_version: str) -> str:
    match = DATASET_VERSION_PATTERN.fullmatch(current_version)
    if not match:
        raise ValueError("Dataset version phải có dạng dataset_vN.")
    return f"dataset_v{int(match.group(1)) + 1}"


def _reject_duplicates(draft: Mapping[str, Any], cases: list[dict[str, Any]]) -> None:
    case_ids = [str(case.get("case_id") or "").strip() for case in cases]
    duplicates = sorted(case_id for case_id, count in Counter(case_ids).items() if case_id and count > 1)
    if duplicates:
        raise ValueError(f"duplicate case_id: {', '.join(duplicates)}.")
    labels = [
        (str(case.get("case_id") or ""), str(case.get("resolved_label") or ""))
        for case in cases
    ]
    if len(labels) != len(set(labels)):
        raise ValueError("duplicate label record trong draft.")
    exported_items = draft.get("exported_items", [])
    if not isinstance(exported_items, list):
        raise ValueError("exported_items phải là list.")
    export_case_ids = [
        str(item.get("case_id") or "").strip()
        for item in exported_items
        if isinstance(item, Mapping)
    ]
    duplicates_export = sorted(
        case_id for case_id, count in Counter(export_case_ids).items() if case_id and count > 1
    )
    if duplicates_export:
        raise ValueError(f"duplicate export case: {', '.join(duplicates_export)}.")


def _non_negative_int(value: Any, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{label} phải là số nguyên không âm.")
    return value
