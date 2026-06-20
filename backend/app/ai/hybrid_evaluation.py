"""Hybrid matching candidate for evaluation mode.

Phase 8.4 keeps this layer parallel to production scoring. It must not mutate
`match_score`, `final_score`, database state, or benchmark baselines.
"""

from __future__ import annotations

from typing import Any, TypedDict


class HybridEvaluation(TypedDict):
    enabled: bool
    hybrid_score_candidate: float
    rule_based_score: float
    semantic_component: float | None
    taxonomy_component: float
    confidence_adjustment: float
    explanation_notes: list[str]
    production_safe: bool


def build_hybrid_evaluation(
    *,
    rule_based_score: float,
    semantic_insights: dict[str, Any],
    taxonomy_insights: dict[str, Any],
    scoring_breakdown: dict[str, Any],
) -> HybridEvaluation:
    """Build a non-production hybrid score candidate."""

    rule_score = _clamp_score(rule_based_score)
    taxonomy_component, taxonomy_notes = _taxonomy_alignment_component(taxonomy_insights)
    confidence_adjustment = _confidence_adjustment(str(scoring_breakdown.get("confidence", "medium")))
    notes = [
        "Hybrid score candidate chỉ dùng để đánh giá nội bộ, chưa thay thế điểm production.",
        *taxonomy_notes,
    ]

    semantic_similarity = semantic_insights.get("resume_jd_similarity")
    semantic_enabled = bool(semantic_insights.get("enabled")) and isinstance(semantic_similarity, (int, float))

    if not semantic_enabled:
        reason = semantic_insights.get("reason") or "semantic unavailable"
        notes.append(f"Semantic chưa khả dụng ({reason}); candidate hiện mirror điểm rule-based.")
        return {
            "enabled": False,
            "hybrid_score_candidate": rule_score,
            "rule_based_score": rule_score,
            "semantic_component": None,
            "taxonomy_component": taxonomy_component,
            "confidence_adjustment": 0.0,
            "explanation_notes": _dedupe(notes),
            "production_safe": True,
        }

    semantic_component = _clamp_score(float(semantic_similarity) * 100.0)
    candidate = (
        rule_score * 0.70
        + semantic_component * 0.20
        + taxonomy_component * 0.10
        + confidence_adjustment
    )
    notes.append("Công thức thử nghiệm: 70% rule-based, 20% semantic, 10% taxonomy, kèm điều chỉnh confidence nhỏ.")
    return {
        "enabled": True,
        "hybrid_score_candidate": round(_clamp_score(candidate), 1),
        "rule_based_score": rule_score,
        "semantic_component": round(semantic_component, 1),
        "taxonomy_component": round(taxonomy_component, 1),
        "confidence_adjustment": confidence_adjustment,
        "explanation_notes": _dedupe(notes),
        "production_safe": True,
    }


def _taxonomy_alignment_component(taxonomy_insights: dict[str, Any]) -> tuple[float, list[str]]:
    resume = taxonomy_insights.get("resume", {}) if isinstance(taxonomy_insights, dict) else {}
    jd = taxonomy_insights.get("job_description", {}) if isinstance(taxonomy_insights, dict) else {}
    resume_role = str(resume.get("role_family") or "general software")
    jd_role = str(jd.get("role_family") or taxonomy_insights.get("role_family") or "general software")
    resume_stacks = set(_as_strings(resume.get("stack_groups")))
    jd_stacks = set(_as_strings(jd.get("stack_groups")))
    resume_related = set(_as_strings(resume.get("related_skill_suggestions")))
    jd_skills = set(_as_strings(jd.get("normalized_skills")))

    notes: list[str] = []
    role_score = 45.0
    if resume_role == jd_role and jd_role != "general software":
        role_score = 65.0
        notes.append(f"Taxonomy: role family khớp ({resume_role}).")
    elif {resume_role, jd_role} == {"backend", "frontend"}:
        role_score = 25.0
        notes.append("Taxonomy: phát hiện mismatch rõ giữa backend và frontend.")
    elif resume_role == "general software" or jd_role == "general software":
        role_score = 40.0
        notes.append("Taxonomy: role family chưa đủ rõ, chỉ tính alignment ở mức thận trọng.")
    else:
        role_score = 35.0
        notes.append(f"Taxonomy: role family khác nhau ({resume_role} -> {jd_role}).")

    stack_bonus = 0.0
    if jd_stacks:
        stack_overlap = resume_stacks.intersection(jd_stacks)
        if stack_overlap:
            stack_bonus = 25.0
            notes.append(f"Taxonomy: có stack overlap ({', '.join(sorted(stack_overlap)[:3])}).")
        elif resume_stacks:
            stack_bonus = 8.0
            notes.append("Taxonomy: cùng có stack signal nhưng chưa thấy overlap trực tiếp.")
    else:
        stack_bonus = 10.0

    related_bonus = 0.0
    related_overlap = {skill.lower() for skill in resume_related}.intersection({skill.lower() for skill in jd_skills})
    if related_overlap:
        related_bonus = 10.0
        notes.append("Taxonomy: related skills có hỗ trợ nhẹ cho alignment.")

    return _clamp_score(role_score + stack_bonus + related_bonus), notes


def _confidence_adjustment(confidence: str) -> float:
    if confidence == "high":
        return 2.0
    if confidence == "low":
        return -5.0
    return 0.0


def _as_strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item).strip()]


def _clamp_score(value: float) -> float:
    return round(max(0.0, min(100.0, float(value))), 1)


def _dedupe(items: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        key = item.lower()
        if key not in seen:
            result.append(item)
            seen.add(key)
    return result