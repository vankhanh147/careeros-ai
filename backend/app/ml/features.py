"""Feature extraction for the trainable matching prototype.

This module intentionally builds simple text features for TF-IDF and structured
features for offline hybrid model evaluation. It does not touch production
scoring and does not depend on user data.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


FEATURE_FIELDS = (
    "resume_summary",
    "job_description_summary",
    "target_role",
    "role_family",
    "candidate_stack",
    "jd_stack",
    "missing_critical_skills",
    "skill_overlap",
)

HYBRID_STRUCTURED_FEATURE_KEYS = (
    "rule_based_score",
    "skill_score",
    "keyword_score",
    "role_alignment_score",
    "evidence_score",
    "confidence",
    "length_sanity",
    "critical_skill_count",
    "missing_critical_skill_count",
    "matched_skill_count",
    "missing_skill_count",
    "role_family_match",
    "stack_group_match_count",
    "normalized_skill_overlap_count",
    "related_skill_support_count",
    "semantic_available",
    "semantic_similarity",
    "hybrid_score_candidate",
    "taxonomy_component",
    "confidence_adjustment",
    "seniority_level",
    "category",
    "target_role",
    "candidate_stack",
    "jd_stack",
)


def build_matching_feature_text(case: Mapping[str, Any]) -> str:
    """Convert a synthetic/runtime matching payload into one TF-IDF text row."""

    parts: list[str] = []
    for field in FEATURE_FIELDS:
        text = _stringify_feature(case.get(field))
        if text:
            parts.append(f"{field}: {text}")
    return "\n".join(parts).strip()


def build_feature_corpus(cases: Sequence[Mapping[str, Any]]) -> list[str]:
    return [build_matching_feature_text(case) for case in cases]


def build_hybrid_text_input(case: Mapping[str, Any]) -> str:
    return build_matching_feature_text(case)


def build_hybrid_structured_features(case: Mapping[str, Any], analysis_result: Mapping[str, Any]) -> dict[str, Any]:
    scoring = _mapping(analysis_result.get("scoring_breakdown"))
    taxonomy = _mapping(analysis_result.get("taxonomy_insights"))
    hybrid = _mapping(analysis_result.get("hybrid_evaluation"))
    semantic = _mapping(analysis_result.get("semantic_insights"))
    resume_taxonomy = _mapping(taxonomy.get("resume"))
    jd_taxonomy = _mapping(taxonomy.get("job_description"))
    resume_stacks = set(_as_list(scoring.get("resume_stack_groups")))
    jd_stacks = set(_as_list(scoring.get("jd_stack_groups")))
    normalized_resume_skills = set(item.lower() for item in _as_list(resume_taxonomy.get("normalized_skills")))
    normalized_jd_skills = set(item.lower() for item in _as_list(jd_taxonomy.get("normalized_skills")))
    resume_related = set(item.lower() for item in _as_list(resume_taxonomy.get("related_skill_suggestions")))
    jd_related = set(item.lower() for item in _as_list(jd_taxonomy.get("related_skill_suggestions")))
    related_support = resume_related.intersection(normalized_jd_skills).union(jd_related.intersection(normalized_resume_skills))
    critical_skills = _as_list(scoring.get("critical_skills"))
    missing_skills = _as_list(analysis_result.get("missing_skills"))
    critical_missing = [skill for skill in critical_skills if skill in set(missing_skills)]

    features: dict[str, Any] = {
        "rule_based_score": _float(analysis_result.get("match_score")),
        "skill_score": _float(scoring.get("skill_score")),
        "keyword_score": _float(scoring.get("keyword_score")),
        "role_alignment_score": _float(scoring.get("role_alignment_score")),
        "evidence_score": _float(scoring.get("evidence_score")),
        "confidence": _confidence_to_number(str(scoring.get("confidence", "medium"))),
        "length_sanity": _float(scoring.get("length_sanity")),
        "critical_skill_count": len(critical_skills),
        "missing_critical_skill_count": len(critical_missing),
        "matched_skill_count": len(_as_list(analysis_result.get("matched_skills"))),
        "missing_skill_count": len(missing_skills),
        "role_family_match": int(str(scoring.get("resume_role_family")) == str(scoring.get("jd_role_family"))),
        "stack_group_match_count": len(resume_stacks.intersection(jd_stacks)),
        "normalized_skill_overlap_count": len(normalized_resume_skills.intersection(normalized_jd_skills)),
        "related_skill_support_count": len(related_support),
        "semantic_available": int(bool(semantic.get("enabled"))),
        "semantic_similarity": _float(semantic.get("resume_jd_similarity")),
        "hybrid_score_candidate": _float(hybrid.get("hybrid_score_candidate")),
        "taxonomy_component": _float(hybrid.get("taxonomy_component")),
        "confidence_adjustment": _float(hybrid.get("confidence_adjustment")),
        "seniority_level": str(case.get("seniority") or ""),
        "category": str(case.get("category") or case.get("group") or ""),
        "target_role": str(case.get("target_role") or ""),
        "candidate_stack": str(case.get("candidate_stack") or ""),
        "jd_stack": str(case.get("jd_stack") or ""),
    }
    return {key: features[key] for key in HYBRID_STRUCTURED_FEATURE_KEYS}


def build_hybrid_training_row(case: Mapping[str, Any], analysis_result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "case_id": str(case.get("case_id") or ""),
        "text_input": build_hybrid_text_input(case),
        "structured_features": build_hybrid_structured_features(case, analysis_result),
        "label": str(case.get("fit_label") or ""),
        "source_category": str(case.get("category") or case.get("group") or ""),
        "expected_score_range": str(case.get("expected_score_range") or ""),
    }


def _stringify_feature(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return ", ".join(str(item).strip() for item in value if str(item).strip())
    return str(value).strip()


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    return [str(item) for item in value if str(item).strip()]


def _float(value: Any) -> float:
    if isinstance(value, bool):
        return float(int(value))
    if isinstance(value, (int, float)):
        return float(value)
    return 0.0


def _confidence_to_number(confidence: str) -> float:
    normalized = confidence.lower()
    if normalized == "high":
        return 1.0
    if normalized == "low":
        return 0.0
    return 0.5
