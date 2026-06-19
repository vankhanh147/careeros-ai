"""Read-only taxonomy insight helpers for CareerOS AI.

Phase 8.2 uses this layer in parallel with production scoring. The helpers here
must not mutate matcher scores or database state.
"""

from __future__ import annotations

from typing import TypedDict

from app.ai.role_taxonomy import ROLE_TAXONOMY
from app.ai.skill_graph import SKILL_GRAPH, normalize_skill_alias, related_skills


class TaxonomyInsight(TypedDict):
    """Normalized taxonomy metadata for one skill set."""

    role_family: str
    stack_groups: list[str]
    normalized_skills: list[str]
    related_skill_suggestions: list[str]


class MatchTaxonomyInsights(TypedDict):
    """Taxonomy metadata returned alongside analysis results."""

    role_family: str
    stack_groups: list[str]
    normalized_skills: list[str]
    related_skill_suggestions: list[str]
    resume: TaxonomyInsight
    job_description: TaxonomyInsight


ROLE_PRIORITY = [
    "backend",
    "frontend",
    "fullstack",
    "mobile",
    "ai/data",
    "data",
    "devops",
    "qa/testing",
    "cybersecurity",
]


def normalize_skill_name(skill: str) -> str:
    """Return canonical skill name if known, otherwise preserve readable input."""

    normalized = normalize_skill_alias(skill)
    if normalized:
        return normalized
    cleaned = " ".join(str(skill).strip().split())
    return cleaned


def normalize_skill_list(skills: list[str]) -> list[str]:
    """Normalize skill aliases while preserving stable order."""

    return _dedupe([normalize_skill_name(skill) for skill in skills if str(skill).strip()])


def build_taxonomy_insight(skills: list[str]) -> TaxonomyInsight:
    """Build read-only taxonomy metadata for a list of detected skills."""

    normalized_skills = normalize_skill_list(skills)
    role_family = _infer_role_family(normalized_skills)
    stack_groups = _infer_stack_groups(normalized_skills, role_family)
    suggestions = _related_skill_suggestions(normalized_skills, role_family)
    return {
        "role_family": role_family,
        "stack_groups": stack_groups,
        "normalized_skills": normalized_skills,
        "related_skill_suggestions": suggestions,
    }


def build_match_taxonomy_insights(resume_skills: list[str], jd_skills: list[str]) -> MatchTaxonomyInsights:
    """Build parallel taxonomy metadata for a Resume/JD pair."""

    resume = build_taxonomy_insight(resume_skills)
    job_description = build_taxonomy_insight(jd_skills)
    combined_skills = normalize_skill_list([*resume["normalized_skills"], *job_description["normalized_skills"]])
    combined = build_taxonomy_insight(combined_skills)
    target_role_family = job_description["role_family"] if jd_skills else combined["role_family"]
    return {
        "role_family": target_role_family,
        "stack_groups": _dedupe([*job_description["stack_groups"], *resume["stack_groups"]]),
        "normalized_skills": combined["normalized_skills"],
        "related_skill_suggestions": _dedupe([
            *job_description["related_skill_suggestions"],
            *resume["related_skill_suggestions"],
        ])[:12],
        "resume": resume,
        "job_description": job_description,
    }


def expand_related_skills(skills: list[str], limit: int = 6) -> list[str]:
    """Return related skills for a skill list without duplicating existing skills."""

    normalized = normalize_skill_list(skills)
    return _related_skill_suggestions(normalized, _infer_role_family(normalized), limit=limit)


def _infer_role_family(normalized_skills: list[str]) -> str:
    skill_set = {skill.lower() for skill in normalized_skills}
    frontend_markers = {"react", "next.js", "angular", "vue", "tailwind css", "html", "css", "typescript", "javascript"}
    backend_markers = {"fastapi", "django", "flask", "node.js", "express", "asp.net core", ".net", "c#", "spring boot"}
    ai_markers = {"machine learning", "nlp", "sentence transformers", "pytorch", "tensorflow", "scikit-learn"}
    mobile_markers = {"flutter", "dart", "react native", "android", "kotlin", "ios", "swift"}
    devops_markers = {"docker", "kubernetes", "ci/cd", "terraform", "aws", "azure", "gcp"}

    if skill_set.intersection(frontend_markers) and not skill_set.intersection(backend_markers):
        return "frontend"
    if skill_set.intersection(backend_markers) and not skill_set.intersection(frontend_markers):
        return "backend"
    if skill_set.intersection(frontend_markers) and skill_set.intersection(backend_markers):
        return "fullstack"
    if skill_set.intersection(ai_markers):
        return "ai/data"
    if skill_set.intersection(mobile_markers):
        return "mobile"
    if skill_set.intersection(devops_markers) and len(skill_set) <= 4:
        return "devops"

    scores: dict[str, int] = {}
    for role in ROLE_TAXONOMY.values():
        family = role["role_family"]
        common = {skill.lower() for skill in role["common_skills"]}
        score = len(skill_set.intersection(common))
        if score:
            scores[family] = scores.get(family, 0) + score
    if not scores:
        return "general software"
    return sorted(scores.items(), key=lambda item: (-item[1], _role_rank(item[0])))[0][0]


def _infer_stack_groups(normalized_skills: list[str], role_family: str) -> list[str]:
    skill_set = {skill.lower() for skill in normalized_skills}
    detected: list[str] = []
    for role in ROLE_TAXONOMY.values():
        if role_family != "general software" and role["role_family"] != role_family:
            continue
        common = {skill.lower() for skill in role["common_skills"]}
        if skill_set.intersection(common):
            detected.extend(role["stack_groups"])
    return _dedupe(detected)[:8]


def _related_skill_suggestions(normalized_skills: list[str], role_family: str, limit: int = 8) -> list[str]:
    existing = {skill.lower() for skill in normalized_skills}
    suggestions: list[str] = []
    for skill in normalized_skills:
        for related in related_skills(skill):
            if related.lower() not in existing:
                suggestions.append(related)
    role_common = _common_skills_for_family(role_family)
    for skill in role_common:
        if skill.lower() not in existing:
            suggestions.append(skill)
    return _dedupe(suggestions)[:limit]


def _common_skills_for_family(role_family: str) -> list[str]:
    skills: list[str] = []
    for role in ROLE_TAXONOMY.values():
        if role["role_family"] == role_family:
            skills.extend(role["common_skills"])
    return _dedupe(skills)


def _role_rank(role_family: str) -> int:
    try:
        return ROLE_PRIORITY.index(role_family)
    except ValueError:
        return len(ROLE_PRIORITY)


def _dedupe(items: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        cleaned = " ".join(str(item).strip().split())
        key = cleaned.lower()
        if cleaned and key not in seen:
            result.append(cleaned)
            seen.add(key)
    return result
