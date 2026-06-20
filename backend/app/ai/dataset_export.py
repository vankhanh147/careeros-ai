import json
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.models.match_analysis import MatchAnalysis
from app.models.user_feedback import UserFeedback


DATASET_SCHEMA_VERSION = "careeros-dataset-v1"


def build_analysis_summary(analysis: MatchAnalysis) -> dict[str, Any]:
    """Export analysis metadata without CV/JD text or user PII."""
    return {
        "analysis_id": analysis.id,
        "user_id": analysis.user_id,
        "resume_id": analysis.resume_id,
        "job_description_id": analysis.job_description_id,
        "actual_score": float(analysis.match_score),
        "matched_skills": _load_json_list(analysis.matched_skills),
        "missing_skills": _load_json_list(analysis.missing_skills),
        "keyword_overlap": _load_json_list(analysis.keyword_overlap),
        "created_at": _isoformat(analysis.created_at),
    }


def build_feedback_label(
    feedback: UserFeedback,
    *,
    case_id: str | None = None,
    expected_score_range: str | None = None,
    disagreement_notes: str | None = None,
) -> dict[str, Any]:
    agreed = bool(feedback.useful)
    return {
        "case_id": case_id,
        "feedback_id": feedback.id,
        "user_id": feedback.user_id,
        "feedback_type": feedback.feedback_type,
        "user_agreed": agreed,
        "user_disagreed": not agreed,
        "reason": feedback.comment,
        "expected_score_range": expected_score_range,
        "disagreement_notes": disagreement_notes,
        "created_at": _isoformat(feedback.created_at),
    }


def build_benchmark_case(
    *,
    case_id: str,
    role_family: str,
    candidate_stack: str,
    target_role: str,
    expected_fit: str,
    actual_score: float | None,
    confidence: str | None,
    review_notes: str,
) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "role_family": role_family,
        "candidate_stack": candidate_stack,
        "target_role": target_role,
        "expected_fit": expected_fit,
        "actual_score": actual_score,
        "confidence": confidence,
        "review_notes": review_notes,
    }


def build_dataset_payload(
    *,
    dataset_name: str,
    benchmark_cases: Sequence[Mapping[str, Any]] | None = None,
    feedback_labels: Sequence[Mapping[str, Any]] | None = None,
    analysis_summaries: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": DATASET_SCHEMA_VERSION,
        "dataset_name": dataset_name,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "benchmark_cases": list(benchmark_cases or []),
        "feedback_labels": list(feedback_labels or []),
        "analysis_summaries": list(analysis_summaries or []),
    }


def write_dataset_json(payload: Mapping[str, Any], output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_json_list(value: str | None) -> list[str]:
    if not value:
        return []
    try:
        parsed = json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return []
    if not isinstance(parsed, list):
        return []
    return [str(item) for item in parsed]


def _isoformat(value: Any) -> str | None:
    if isinstance(value, datetime):
        return value.isoformat()
    return None
