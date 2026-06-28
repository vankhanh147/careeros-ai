"""QA bridge cho Shadow Label Review Draft.

Bridge chỉ đọc draft, gọi validator Phase 10.2 và tạo readiness summary.
Module không sửa draft, không approve label và không promote dataset.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from app.ml.training_infra import validate_label_review_cases


def read_json(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError(f"File JSON phải là object: {path}")
    return payload


def write_json(path: str | Path, payload: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_no_draft_summary(*, source_draft: str) -> dict[str, Any]:
    return {
        "status": "no_draft",
        "source_draft": source_draft,
        "total_cases": 0,
        "errors_count": 0,
        "warnings_count": 0,
        "ready_for_review": False,
        "ready_for_promotion_count": 0,
        "ready_for_promotion": False,
        "not_ready": True,
        "promotion_blockers": ["NO_DRAFT"],
        "case_results": [],
        "recommendation": "run shadow review resolution export first",
        "draft_modified": False,
        "promotion_allowed": False,
        "training_allowed": False,
    }


def evaluate_label_review_draft(
    *,
    draft: Mapping[str, Any],
    source_draft: str,
) -> dict[str, Any]:
    cases_value = draft.get("cases")
    if not isinstance(cases_value, list):
        raise ValueError("Label Review Draft thiếu field cases dạng list.")
    cases = [dict(case) for case in cases_value if isinstance(case, Mapping)]
    if len(cases) != len(cases_value):
        raise ValueError("Mỗi Label Review Draft case phải là JSON object.")

    validation = validate_label_review_cases(cases)
    total_cases = int(validation["total_cases"])
    errors_count = int(validation["errors_count"])
    warnings_count = int(validation["warnings_count"])
    ready_count = int(validation["ready_for_promotion_count"])
    ready_for_review = total_cases > 0 and errors_count == 0
    ready_for_promotion = bool(validation["ready_for_promotion"])
    not_ready = total_cases == 0 or errors_count > 0
    blockers = build_promotion_blockers(cases, validation)

    if ready_for_promotion:
        status = "ready_for_promotion_planning"
        recommendation = (
            "Draft đủ điều kiện lập Dataset Promotion plan; bridge không tự động promote."
        )
    elif ready_for_review:
        status = "ready_for_review"
        recommendation = (
            "Draft hợp lệ để tiếp tục human review nhưng chưa đủ điều kiện Dataset Promotion."
        )
    else:
        status = "not_ready"
        recommendation = "Sửa toàn bộ validation errors trước khi tiếp tục Label Review."

    return {
        "status": status,
        "source_draft": source_draft,
        "export_id": draft.get("export_id"),
        "total_cases": total_cases,
        "errors_count": errors_count,
        "warnings_count": warnings_count,
        "ready_for_review": ready_for_review,
        "ready_for_promotion_count": ready_count,
        "ready_for_promotion": ready_for_promotion,
        "not_ready": not_ready,
        "promotion_blockers": blockers,
        "case_results": validation["case_results"],
        "recommendation": recommendation,
        "draft_modified": False,
        "promotion_allowed": False,
        "training_allowed": False,
    }


def build_promotion_blockers(
    cases: list[dict[str, Any]],
    validation: Mapping[str, Any],
) -> list[str]:
    blockers: list[str] = []
    if not cases:
        blockers.append("NO_CASES")
    if int(validation.get("errors_count", 0)) > 0:
        blockers.append("VALIDATION_ERRORS")
    if int(validation.get("ready_for_promotion_count", 0)) == 0:
        blockers.append("NO_PROMOTION_READY_CASES")
    for case in cases:
        case_id = str(case.get("case_id") or "unknown")
        status = str(case.get("review_status") or "")
        if case.get("approved_for_training") is True and status not in {
            "APPROVED",
            "PROMOTED",
            "TRAINABLE",
        }:
            blockers.append(f"{case_id}:INVALID_TRAINING_APPROVAL")
        if case.get("anonymized") is not True:
            blockers.append(f"{case_id}:NOT_ANONYMIZED")
        if status in {"UNDER_REVIEW", "APPROVED", "PROMOTED", "TRAINABLE"} and not str(
            case.get("reviewer") or ""
        ).strip():
            blockers.append(f"{case_id}:MISSING_REVIEWER")
        confidence = case.get("label_confidence")
        if (
            not isinstance(confidence, (int, float))
            or isinstance(confidence, bool)
            or not 0 <= float(confidence) <= 1
        ):
            blockers.append(f"{case_id}:INVALID_LABEL_CONFIDENCE")
    return list(dict.fromkeys(blockers))
