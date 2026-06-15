import re
import unicodedata
from typing import Any

from app.models.career_profile import CareerProfile
from app.services.resume_job_matcher import ROLE_CORE_SKILLS, extract_skills

DEFAULT_TARGET_ROLE = "target technology role"


def infer_week_count(timeline: str | None) -> int:
    raw = (timeline or "").strip().lower()
    normalized = unicodedata.normalize("NFKD", raw).encode("ascii", "ignore").decode("ascii")
    number_match = re.search(r"(\d+)", normalized)
    if not number_match:
        return 6

    value = max(1, int(number_match.group(1)))
    if any(token in normalized for token in ("tuan", "week", "weeks")) or "tu" in raw:
        return value
    if any(token in normalized for token in ("thang", "month", "months")) or "th" in raw:
        return value * 4
    return 6


def _item_count_for_timeline(week_count: int) -> int:
    if week_count <= 2:
        return week_count
    if week_count <= 4:
        return week_count
    if week_count >= 8:
        return min(8, max(6, week_count))
    return week_count


def build_roadmap_from_analysis(
    *,
    target_role: str,
    current_level: str,
    timeline: str,
    prioritized_missing_skills: dict[str, list[str]],
    improvement_plan: list[str],
    critical_skills: list[str] | None = None,
    confidence: str = "medium",
    resume_feedback: dict[str, Any] | None = None,
    role_family: str = "",
    stack_groups: list[str] | None = None,
) -> dict[str, object]:
    week_count = infer_week_count(timeline)
    item_count = _item_count_for_timeline(week_count)
    target_role = target_role.strip() or DEFAULT_TARGET_ROLE
    current_level = current_level.strip() or "not specified"
    high = prioritized_missing_skills.get("high_priority", [])
    medium = prioritized_missing_skills.get("medium_priority", [])
    low = prioritized_missing_skills.get("low_priority", [])
    critical = critical_skills or []
    skill_queue = _dedupe([skill for skill in critical if skill in high + medium + low] + high + medium + low)

    feedback_hints = _feedback_hints(resume_feedback)
    items = _build_items(
        item_count=item_count,
        target_role=target_role,
        current_level=current_level,
        skill_queue=skill_queue,
        high_priority=set(high).union(critical),
        medium_priority=set(medium),
        improvement_plan=improvement_plan,
        personalized=True,
        feedback_hints=feedback_hints,
    )
    gap_text = _gap_summary(high, medium, low)
    stack_text = f" Stack focus: {', '.join(stack_groups or [])}." if stack_groups else ""
    confidence_text = " Personalization confidence is lower, so verify the CV/JD preview before following every step." if confidence == "low" else ""
    return {
        "title": f"Roadmap {week_count} tu?n cho {target_role}",
        "target_role": target_role,
        "timeline": timeline or f"{week_count} tu?n",
        "items": items,
        "summary": f"Roadmap V2 focuses on {gap_text}. It is designed to help you learn the right skill gaps, create CV evidence and prepare interview answers for {target_role}.{stack_text}{confidence_text}",
    }


def build_roadmap_from_profile(profile: CareerProfile, timeline: str | None = None) -> dict[str, object]:
    selected_timeline = (timeline or profile.timeline or "").strip()
    week_count = infer_week_count(selected_timeline)
    item_count = _item_count_for_timeline(week_count)
    target_role = profile.target_role.strip() or DEFAULT_TARGET_ROLE
    current_level = profile.current_level.strip() or "not specified"
    profile_text = " ".join(
        [
            profile.skills or "",
            profile.experience_summary or "",
            profile.projects_summary or "",
            profile.career_goal or "",
            target_role,
        ]
    )
    current_skills = set(extract_skills(profile_text))
    role_context = _detect_role_context(target_role)
    core_skills = _core_skills_for_roles(role_context)
    missing_skills = [skill for skill in core_skills if skill not in current_skills]

    if not missing_skills and current_skills:
        missing_skills = _fallback_growth_skills(role_context, current_skills)

    high_priority = set(missing_skills[:3])
    improvement_plan = [_generic_skill_action(skill) for skill in missing_skills[:6]]
    if not improvement_plan:
        improvement_plan = [
            "Review your CV/profile and clarify project scope, personal responsibility, tech stack and real output.",
            "Pick one project close to your target role and rewrite it as a short case study: problem, implementation, output and lessons learned.",
        ]

    items = _build_items(
        item_count=item_count,
        target_role=target_role,
        current_level=current_level,
        skill_queue=missing_skills,
        high_priority=high_priority,
        medium_priority=set(missing_skills[3:6]),
        improvement_plan=improvement_plan,
        personalized=False,
        feedback_hints=[],
    )
    return {
        "title": f"Roadmap {week_count} tu?n cho {target_role}",
        "target_role": target_role,
        "timeline": selected_timeline or f"{week_count} tu?n",
        "items": items,
        "summary": f"Basic roadmap generated from career profile only. Personalization is lower because no Resume/JD analysis was selected. Focus: move from {current_level} toward {target_role} through practical tasks, CV evidence and interview preparation.",
    }


def _build_items(
    *,
    item_count: int,
    target_role: str,
    current_level: str,
    skill_queue: list[str],
    high_priority: set[str],
    medium_priority: set[str],
    improvement_plan: list[str],
    personalized: bool,
    feedback_hints: list[str],
) -> list[dict[str, object]]:
    items = []
    clean_skills = skill_queue or []
    actions = improvement_plan or []

    for index in range(item_count):
        week_number = index + 1
        focus_skills = _skills_for_week(clean_skills, index, item_count)
        priority = _priority_for_skills(focus_skills, high_priority, medium_priority)
        if focus_skills:
            learning_focus = _learning_focus_for_skills(focus_skills, target_role, priority)
            item_actions = _actions_for_week(focus_skills, actions, target_role, current_level)
            practice_task = _practice_task_for_skills(focus_skills, target_role)
            cv_evidence_output = _cv_evidence_for_skills(focus_skills, target_role)
            interview_prep = _interview_questions_for_skills(focus_skills, target_role)
            expected_output = _expected_output_for_skills(focus_skills, target_role)
        else:
            learning_focus = _fallback_focus(week_number, item_count, target_role, personalized)
            item_actions = _fallback_actions(week_number, target_role)
            practice_task = _fallback_practice_task(week_number, target_role)
            cv_evidence_output = _fallback_cv_evidence(week_number, target_role)
            interview_prep = _fallback_interview_questions(target_role)
            expected_output = _fallback_expected_output(week_number, item_count, target_role)

        if feedback_hints and week_number == 1:
            item_actions = _dedupe(item_actions + feedback_hints[:2])[:4]

        items.append(
            {
                "week": f"Tu?n {week_number}",
                "focus": learning_focus,
                "learning_focus": learning_focus,
                "skills": focus_skills,
                "actions": item_actions,
                "practice_task": practice_task,
                "cv_evidence_output": cv_evidence_output,
                "interview_prep": interview_prep,
                "priority": priority,
                "expected_output": expected_output,
            }
        )

    return items


def _skills_for_week(skills: list[str], index: int, item_count: int) -> list[str]:
    if not skills:
        return []
    if len(skills) <= item_count:
        return [skills[index]] if index < len(skills) else []
    chunk_size = max(1, (len(skills) + item_count - 1) // item_count)
    start = index * chunk_size
    return skills[start : start + chunk_size]


def _priority_for_skills(skills: list[str], high_priority: set[str], medium_priority: set[str]) -> str:
    if any(skill in high_priority for skill in skills):
        return "high"
    if any(skill in medium_priority for skill in skills):
        return "medium"
    return "low"


def _learning_focus_for_skills(skills: list[str], target_role: str, priority: str) -> str:
    skill_text = ", ".join(skills)
    if priority == "high":
        return f"High-priority focus: learn and prove {skill_text} because it is important for {target_role}."
    if priority == "medium":
        return f"Strengthen {skill_text} so your CV evidence is closer to {target_role} responsibilities."
    return f"Polish supporting skill(s): {skill_text}, mainly to improve CV/JD alignment."


def _actions_for_week(skills: list[str], improvement_plan: list[str], target_role: str, current_level: str) -> list[str]:
    selected_actions = []
    for skill in skills:
        matching_action = next((action for action in improvement_plan if skill.lower() in action.lower()), None)
        selected_actions.append(matching_action or _generic_skill_action(skill))

    selected_actions.append(
        f"Create a small artifact that proves this skill for {target_role}: commit, README, API route, UI screen, notebook or test case."
    )
    if current_level.lower() in {"fresher", "junior", "beginner", "entry level", "intern"}:
        selected_actions.append("Write a short README: problem, approach, mistakes fixed and what you can explain in interview.")
    return _dedupe(selected_actions)[:4]


def _practice_task_for_skills(skills: list[str], target_role: str) -> str:
    skill_set = set(skills)
    if {"authentication", "jwt", "oauth"}.intersection(skill_set):
        return "Build login/register, one protected endpoint and one role-based authorization check."
    if {"api", "rest api", "fastapi", "django", "flask", "node.js", "express", "asp.net core"}.intersection(skill_set):
        return "Build a small CRUD API with validation, error responses and a short endpoint README."
    if {"database", "sql", "postgresql", "mysql", "mongodb"}.intersection(skill_set):
        return "Design a small schema, seed sample data and write 3-5 queries used by a real feature."
    if {"react", "next.js", "typescript", "javascript", "tailwind", "html", "css"}.intersection(skill_set):
        return "Build one responsive UI flow with form state, API integration, loading state and error state."
    if {"docker", "ci/cd", "github", "git"}.intersection(skill_set):
        return "Package or document the project setup so another developer can run it locally from the README."
    if {"ai", "machine learning", "nlp", "scikit-learn", "pandas", "numpy"}.intersection(skill_set):
        return "Create a mini notebook or script with dataset prep, baseline model/analysis and clear result notes."
    return f"Create one mini-task connected to {target_role} that proves {', '.join(skills) or 'your target skill'} in a real artifact."


def _cv_evidence_for_skills(skills: list[str], target_role: str) -> str:
    skill_text = ", ".join(skills) or "the target skill"
    if {"authentication", "jwt", "oauth"}.intersection(skills):
        return "If you complete this task, you can add: 'Implemented authentication/JWT flow for protected API endpoints.'"
    if {"api", "rest api", "fastapi", "asp.net core", "node.js", "express"}.intersection(skills):
        return "If accurate, add a bullet about building API endpoints with validation, error handling and data integration."
    if {"database", "sql", "postgresql", "mysql", "mongodb"}.intersection(skills):
        return "If accurate, add a bullet about schema/query work and how the database supported a feature."
    if {"react", "next.js", "typescript", "tailwind"}.intersection(skills):
        return "If accurate, add a bullet about building responsive UI and integrating it with REST APIs."
    return f"If you actually complete a project task with {skill_text}, add one CV bullet that states the feature, your responsibility and the artifact produced."


def _interview_questions_for_skills(skills: list[str], target_role: str) -> list[str]:
    questions = []
    for skill in skills[:2]:
        if skill in {"authentication", "jwt", "oauth"}:
            questions.extend(["How does JWT authentication work?", "How would you protect an endpoint by role?"])
        elif skill in {"api", "rest api", "fastapi", "asp.net core", "node.js", "express"}:
            questions.extend(["How do you design a clean API endpoint?", "How do you handle validation and errors?"])
        elif skill in {"database", "sql", "postgresql", "mysql", "mongodb"}:
            questions.extend(["How would you design the schema for this feature?", "How do you avoid inefficient queries?"])
        elif skill in {"react", "next.js", "typescript", "javascript"}:
            questions.extend(["How do you manage loading and error states in UI?", "How do components call backend APIs safely?"])
        elif skill in {"docker", "ci/cd"}:
            questions.extend(["Why use Docker for local development or deployment?", "How would you debug a container that fails to start?"])
        else:
            questions.append(f"How have you applied {skill} in a real project?")
    return _dedupe(questions)[:2] or [f"What did you build that proves readiness for {target_role}?"]


def _expected_output_for_skills(skills: list[str], target_role: str) -> str:
    return f"A concrete artifact for {', '.join(skills)}: commit, README, demo, test case or CV bullet aligned with {target_role}."


def _fallback_focus(week_number: int, item_count: int, target_role: str, personalized: bool) -> str:
    if not personalized and week_number == 1:
        return f"Clarify the baseline requirements for {target_role} because no analysis was selected."
    if week_number == item_count:
        return f"Finalize CV alignment and interview story for {target_role}."
    if week_number == 1:
        return f"Identify the strongest project evidence for {target_role}."
    return f"Strengthen one project so it better proves readiness for {target_role}."


def _fallback_actions(week_number: int, target_role: str) -> list[str]:
    if week_number == 1:
        return [
            f"Read 2-3 real JDs for {target_role} and list repeated requirements.",
            "Compare those requirements with your CV/profile and choose one gap to prove first.",
        ]
    return [
        "Rewrite one project using: problem, tech stack, personal responsibility and output.",
        "Add only keywords that reflect real work, not skills you have not used.",
    ]


def _fallback_practice_task(week_number: int, target_role: str) -> str:
    if week_number == 1:
        return f"Create a one-page checklist of the top 5 requirements for {target_role} and map each to your current CV evidence."
    return "Improve one existing project artifact: README, demo flow, test case, API endpoint, UI state or notebook explanation."


def _fallback_cv_evidence(week_number: int, target_role: str) -> str:
    if week_number == 1:
        return "No new claim yet. Produce a gap checklist and identify which existing project can support the target role."
    return f"If the improved project evidence is real, add one concise CV bullet aligned with {target_role}. Do not invent metrics."


def _fallback_interview_questions(target_role: str) -> list[str]:
    return [
        f"Which project best proves your fit for {target_role}?",
        "What technical tradeoff or bug can you explain clearly from that project?",
    ]



def _fallback_expected_output(week_number: int, item_count: int, target_role: str) -> str:
    if week_number == item_count:
        return f"Updated CV/profile section and a short interview story for {target_role}."
    return "One improved project artifact or experience bullet that is clearer, safer and closer to the target JD."

def _detect_role_context(text: str) -> list[str]:
    normalized = (text or "").lower()
    roles = []
    if any(token in normalized for token in ("fullstack", "full-stack", "full stack")):
        roles.append("fullstack")
    if any(token in normalized for token in ("backend", "back-end", "back end", "api", "server")):
        roles.append("backend")
    if any(token in normalized for token in ("frontend", "front-end", "front end", "react", "next")):
        roles.append("frontend")
    if any(token in normalized for token in ("ai", "machine learning", "ml", "nlp", "data")):
        roles.append("ai")
    return roles or ["backend", "frontend"]


def _core_skills_for_roles(roles: list[str]) -> list[str]:
    skills = []
    for role in roles:
        skills.extend(sorted(ROLE_CORE_SKILLS.get(role, set())))
    return _dedupe(skills)[:10]


def _fallback_growth_skills(roles: list[str], current_skills: set[str]) -> list[str]:
    candidates = _core_skills_for_roles(roles)
    return [skill for skill in candidates if skill not in current_skills][:6]


def _generic_skill_action(skill: str) -> str:
    if skill in {"docker", "git", "github", "ci/cd"}:
        return f"Apply {skill} in a practical way: setup, local run command, common error and README note."
    if skill in {"rest api", "api", "fastapi", "django", "flask", "node.js", "express", "asp.net core"}:
        return f"Build a small {skill} flow: CRUD, validation, error handling and endpoint documentation."
    if skill in {"postgresql", "mysql", "mongodb", "sql", "database"}:
        return f"Create a database example for {skill}: schema, main query and feature integration."
    if skill in {"authentication", "jwt", "oauth"}:
        return f"Implement a small auth flow with {skill}: login, protected route and common permission error."
    if skill in {"react", "next.js", "typescript", "javascript", "tailwind", "html", "css"}:
        return f"Create or improve a small UI with {skill}: form, state, API integration and responsive layout."
    if skill in {"ai", "machine learning", "nlp", "scikit-learn", "pytorch", "tensorflow"}:
        return f"Build a mini {skill} notebook/project: input data, simple metric and explainable result."
    return f"Learn {skill} through a concrete output: notes, lab, commit or project artifact."


def _feedback_hints(resume_feedback: dict[str, Any] | None) -> list[str]:
    if not isinstance(resume_feedback, dict):
        return []
    hints = []
    for group_name in ("critical_gaps", "missing_evidence_areas", "recommended_next_edits"):
        for item in resume_feedback.get(group_name, []) or []:
            if isinstance(item, dict):
                message = item.get("suggested_edit") or item.get("message")
                if message:
                    hints.append(str(message))
    return _dedupe(hints)


def _gap_summary(high: list[str], medium: list[str], low: list[str]) -> str:
    total = len(high) + len(medium) + len(low)
    if total == 0:
        return "CV alignment and evidence clarity because no major skill gap was detected"
    if high:
        return f"{total} skill gaps, with highest priority on {', '.join(high[:3])}"
    if medium:
        return f"{total} skill gaps, focused on medium-priority skills: {', '.join(medium[:4])}"
    return f"{total} low-priority gaps for CV alignment: {', '.join(low[:4])}"


def _dedupe(items: list[str]) -> list[str]:
    result = []
    seen = set()
    for item in items:
        normalized = item.strip()
        if normalized and normalized not in seen:
            result.append(normalized)
            seen.add(normalized)
    return result
