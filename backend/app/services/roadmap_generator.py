import re
import unicodedata
from typing import Any

from app.ai.taxonomy_insights import expand_related_skills, normalize_skill_list
from app.models.career_profile import CareerProfile
from app.services.resume_job_matcher import ROLE_CORE_SKILLS, extract_skills

DEFAULT_TARGET_ROLE = "vai tr\u00f2 c\u00f4ng ngh\u1ec7 m\u1ee5c ti\u00eau"


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
    current_level = current_level.strip() or "ch\u01b0a x\u00e1c \u0111\u1ecbnh"
    high = normalize_skill_list(prioritized_missing_skills.get("high_priority", []))
    medium = normalize_skill_list(prioritized_missing_skills.get("medium_priority", []))
    low = normalize_skill_list(prioritized_missing_skills.get("low_priority", []))
    critical = normalize_skill_list(critical_skills or [])
    skill_queue = normalize_skill_list([skill for skill in critical if skill in high + medium + low] + high + medium + low)
    related_support_skills = expand_related_skills(skill_queue, limit=4)

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
        related_support_skills=related_support_skills,
    )
    gap_text = _gap_summary(high, medium, low)
    stack_text = f" Tr\u1ecdng t\u00e2m tech stack: {', '.join(stack_groups or [])}." if stack_groups else ""
    confidence_text = " \u0110\u1ed9 tin c\u1eady c\u00e1 nh\u00e2n h\u00f3a \u0111ang th\u1ea5p, h\u00e3y ki\u1ec3m tra l\u1ea1i ph\u1ea7n preview CV/JD tr\u01b0\u1edbc khi l\u00e0m theo t\u1eebng b\u01b0\u1edbc." if confidence == "low" else ""
    return {
        "title": f"Roadmap {week_count} tu\u1ea7n cho {target_role}",
        "target_role": target_role,
        "timeline": timeline or f"{week_count} tu\u1ea7n",
        "items": items,
        "summary": f"Roadmap V2 t\u1eadp trung v\u00e0o {gap_text}. K\u1ebf ho\u1ea1ch n\u00e0y gi\u00fap b\u1ea1n h\u1ecdc \u0111\u00fang skill gap, t\u1ea1o minh ch\u1ee9ng c\u00f3 th\u1ec3 \u0111\u01b0a v\u00e0o CV v\u00e0 chu\u1ea9n b\u1ecb c\u00e2u tr\u1ea3 l\u1eddi ph\u1ecfng v\u1ea5n cho {target_role}.{stack_text}{confidence_text}",
    }


def build_roadmap_from_profile(profile: CareerProfile, timeline: str | None = None) -> dict[str, object]:
    selected_timeline = (timeline or profile.timeline or "").strip()
    week_count = infer_week_count(selected_timeline)
    item_count = _item_count_for_timeline(week_count)
    target_role = profile.target_role.strip() or DEFAULT_TARGET_ROLE
    current_level = profile.current_level.strip() or "ch\u01b0a x\u00e1c \u0111\u1ecbnh"
    profile_text = " ".join(
        [
            profile.skills or "",
            profile.experience_summary or "",
            profile.projects_summary or "",
            profile.career_goal or "",
            target_role,
        ]
    )
    current_skills = set(normalize_skill_list(extract_skills(profile_text)))
    role_context = _detect_role_context(target_role)
    core_skills = _core_skills_for_roles(role_context)
    missing_skills = normalize_skill_list([skill for skill in core_skills if skill not in current_skills])

    if not missing_skills and current_skills:
        missing_skills = normalize_skill_list(_fallback_growth_skills(role_context, current_skills))

    related_support_skills = expand_related_skills(missing_skills, limit=4)
    high_priority = set(missing_skills[:3])
    improvement_plan = [_generic_skill_action(skill) for skill in missing_skills[:6]]
    if not improvement_plan:
        improvement_plan = [
            "R\u00e0 so\u00e1t CV/profile v\u00e0 l\u00e0m r\u00f5 ph\u1ea1m vi project, tr\u00e1ch nhi\u1ec7m c\u00e1 nh\u00e2n, tech stack v\u00e0 output th\u1ef1c t\u1ebf.",
            "Ch\u1ecdn m\u1ed9t project g\u1ea7n v\u1edbi vai tr\u00f2 m\u1ee5c ti\u00eau v\u00e0 vi\u1ebft l\u1ea1i th\u00e0nh case study ng\u1eafn: b\u00e0i to\u00e1n, c\u00e1ch tri\u1ec3n khai, output v\u00e0 b\u00e0i h\u1ecdc.",
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
        related_support_skills=related_support_skills,
    )
    return {
        "title": f"Roadmap {week_count} tu\u1ea7n cho {target_role}",
        "target_role": target_role,
        "timeline": selected_timeline or f"{week_count} tu\u1ea7n",
        "items": items,
        "summary": f"Roadmap c\u01a1 b\u1ea3n \u0111\u01b0\u1ee3c t\u1ea1o t\u1eeb h\u1ed3 s\u01a1 ngh\u1ec1 nghi\u1ec7p. M\u1ee9c c\u00e1 nh\u00e2n h\u00f3a th\u1ea5p h\u01a1n v\u00ec ch\u01b0a ch\u1ecdn analysis Resume \u2194 JD. Tr\u1ecdng t\u00e2m: \u0111i t\u1eeb m\u1ee9c {current_level} \u0111\u1ebfn {target_role} th\u00f4ng qua b\u00e0i th\u1ef1c h\u00e0nh, minh ch\u1ee9ng cho CV v\u00e0 chu\u1ea9n b\u1ecb ph\u1ecfng v\u1ea5n.",
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
    related_support_skills: list[str] | None = None,
) -> list[dict[str, object]]:
    items = []
    clean_skills = skill_queue or []
    actions = improvement_plan or []
    related_support_skills = related_support_skills or []

    for index in range(item_count):
        week_number = index + 1
        focus_skills = _skills_for_week(clean_skills, index, item_count)
        priority = _priority_for_skills(focus_skills, high_priority, medium_priority)
        if focus_skills:
            learning_focus = _learning_focus_for_skills(focus_skills, target_role, priority)
            item_actions = _actions_for_week(focus_skills, actions, target_role, current_level)
            related_for_week = [skill for skill in related_support_skills if skill not in focus_skills][:2]
            if related_for_week:
                item_actions.append(f"K\u1ef9 n\u0103ng li\u00ean quan n\u00ean tham kh\u1ea3o th\u00eam: {', '.join(related_for_week)}. Ch\u1ec9 \u0111\u01b0a v\u00e0o CV n\u1ebfu b\u1ea1n c\u00f3 evidence th\u1eadt.")
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
                "week": f"Tu\u1ea7n {week_number}",
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
        return f"\u01afu ti\u00ean cao: h\u1ecdc v\u00e0 ch\u1ee9ng minh n\u0103ng l\u1ef1c v\u1edbi {skill_text} v\u00ec \u0111\u00e2y l\u00e0 nh\u00f3m k\u1ef9 n\u0103ng quan tr\u1ecdng cho {target_role}."
    if priority == "medium":
        return f"C\u1ee7ng c\u1ed1 {skill_text} \u0111\u1ec3 minh ch\u1ee9ng trong CV s\u00e1t h\u01a1n v\u1edbi tr\u00e1ch nhi\u1ec7m c\u1ee7a {target_role}."
    return f"Ho\u00e0n thi\u1ec7n k\u1ef9 n\u0103ng h\u1ed7 tr\u1ee3: {skill_text}, ch\u1ee7 y\u1ebfu \u0111\u1ec3 t\u0103ng \u0111\u1ed9 kh\u1edbp gi\u1eefa CV v\u00e0 JD."


def _actions_for_week(skills: list[str], improvement_plan: list[str], target_role: str, current_level: str) -> list[str]:
    selected_actions = []
    for skill in skills:
        matching_action = next((action for action in improvement_plan if skill.lower() in action.lower()), None)
        selected_actions.append(matching_action or _generic_skill_action(skill))

    selected_actions.append(
        f"T\u1ea1o m\u1ed9t artifact nh\u1ecf ch\u1ee9ng minh k\u1ef9 n\u0103ng n\u00e0y cho {target_role}: commit, README, API route, m\u00e0n h\u00ecnh UI, notebook ho\u1eb7c test case."
    )
    if current_level.lower() in {"fresher", "junior", "beginner", "entry level", "intern"}:
        selected_actions.append("Vi\u1ebft README ng\u1eafn: b\u00e0i to\u00e1n, c\u00e1ch ti\u1ebfp c\u1eadn, l\u1ed7i \u0111\u00e3 x\u1eed l\u00fd v\u00e0 ph\u1ea7n b\u1ea1n c\u00f3 th\u1ec3 gi\u1ea3i th\u00edch khi ph\u1ecfng v\u1ea5n.")
    return _dedupe(selected_actions)[:4]


def _practice_task_for_skills(skills: list[str], target_role: str) -> str:
    skill_set = {skill.lower() for skill in skills}
    if {"authentication", "jwt", "oauth"}.intersection(skill_set):
        return "X\u00e2y d\u1ef1ng login/register, m\u1ed9t protected endpoint v\u00e0 m\u1ed9t ki\u1ec3m tra ph\u00e2n quy\u1ec1n theo role."
    if {"api", "rest api", "fastapi", "django", "flask", "node.js", "express", "asp.net core"}.intersection(skill_set):
        return "X\u00e2y d\u1ef1ng m\u1ed9t CRUD API nh\u1ecf c\u00f3 validation, error response v\u00e0 README ng\u1eafn cho endpoint."
    if {"database", "sql", "postgresql", "mysql", "mongodb"}.intersection(skill_set):
        return "Thi\u1ebft k\u1ebf schema nh\u1ecf, seed d\u1eef li\u1ec7u m\u1eabu v\u00e0 vi\u1ebft 3-5 query ph\u1ee5c v\u1ee5 m\u1ed9t t\u00ednh n\u0103ng th\u1ef1c t\u1ebf."
    if {"react", "next.js", "typescript", "javascript", "tailwind", "html", "css"}.intersection(skill_set):
        return "X\u00e2y d\u1ef1ng m\u1ed9t lu\u1ed3ng giao di\u1ec7n responsive c\u00f3 form state, t\u00edch h\u1ee3p API, loading state v\u00e0 error state."
    if {"docker", "ci/cd", "github", "git"}.intersection(skill_set):
        return "\u0110\u00f3ng g\u00f3i ho\u1eb7c document c\u00e1ch setup project \u0111\u1ec3 developer kh\u00e1c c\u00f3 th\u1ec3 ch\u1ea1y local t\u1eeb README."
    if {"ai", "machine learning", "nlp", "scikit-learn", "pandas", "numpy"}.intersection(skill_set):
        return "T\u1ea1o m\u1ed9t notebook ho\u1eb7c script nh\u1ecf c\u00f3 b\u01b0\u1edbc chu\u1ea9n b\u1ecb d\u1eef li\u1ec7u, baseline model/analysis v\u00e0 ghi ch\u00fa k\u1ebft qu\u1ea3 r\u00f5 r\u00e0ng."
    fallback_skill = "k\u1ef9 n\u0103ng m\u1ee5c ti\u00eau"
    return f"T\u1ea1o m\u1ed9t mini-task g\u1eafn v\u1edbi {target_role} \u0111\u1ec3 ch\u1ee9ng minh {', '.join(skills) or fallback_skill} b\u1eb1ng artifact th\u1ef1c t\u1ebf."


def _cv_evidence_for_skills(skills: list[str], target_role: str) -> str:
    skill_text = ", ".join(skills) or "the target skill"
    skill_set = {skill.lower() for skill in skills}
    if {"authentication", "jwt", "oauth"}.intersection(skill_set):
        return "N\u1ebfu ho\u00e0n th\u00e0nh task n\u00e0y, b\u1ea1n c\u00f3 th\u1ec3 th\u00eam bullet: \'Implemented authentication/JWT flow for protected API endpoints.\'"
    if {"api", "rest api", "fastapi", "asp.net core", "node.js", "express"}.intersection(skill_set):
        return "N\u1ebfu \u0111\u00fang v\u1edbi ph\u1ea7n b\u1ea1n \u0111\u00e3 l\u00e0m, h\u00e3y th\u00eam bullet v\u1ec1 vi\u1ec7c x\u00e2y d\u1ef1ng API endpoints c\u00f3 validation, error handling v\u00e0 t\u00edch h\u1ee3p d\u1eef li\u1ec7u."
    if {"database", "sql", "postgresql", "mysql", "mongodb"}.intersection(skill_set):
        return "N\u1ebfu \u0111\u00fang v\u1edbi ph\u1ea7n b\u1ea1n \u0111\u00e3 l\u00e0m, h\u00e3y th\u00eam bullet v\u1ec1 schema/query v\u00e0 c\u00e1ch database h\u1ed7 tr\u1ee3 m\u1ed9t t\u00ednh n\u0103ng c\u1ee5 th\u1ec3."
    if {"react", "next.js", "typescript", "tailwind"}.intersection(skill_set):
        return "N\u1ebfu \u0111\u00fang v\u1edbi ph\u1ea7n b\u1ea1n \u0111\u00e3 l\u00e0m, h\u00e3y th\u00eam bullet v\u1ec1 vi\u1ec7c x\u00e2y d\u1ef1ng UI responsive v\u00e0 t\u00edch h\u1ee3p v\u1edbi REST APIs."
    return f"N\u1ebfu b\u1ea1n th\u1ef1c s\u1ef1 ho\u00e0n th\u00e0nh project task v\u1edbi {skill_text}, h\u00e3y th\u00eam m\u1ed9t CV bullet n\u00eau r\u00f5 t\u00ednh n\u0103ng, tr\u00e1ch nhi\u1ec7m c\u1ee7a b\u1ea1n v\u00e0 artifact \u0111\u00e3 t\u1ea1o."


def _interview_questions_for_skills(skills: list[str], target_role: str) -> list[str]:
    questions = []
    for skill in skills[:2]:
        normalized_skill = skill.lower()
        if normalized_skill in {"authentication", "jwt", "oauth"}:
            questions.extend(["JWT authentication ho\u1ea1t \u0111\u1ed9ng nh\u01b0 th\u1ebf n\u00e0o?", "B\u1ea1n s\u1ebd b\u1ea3o v\u1ec7 endpoint theo role nh\u01b0 th\u1ebf n\u00e0o?"])
        elif normalized_skill in {"api", "rest api", "fastapi", "asp.net core", "node.js", "express"}:
            questions.extend(["B\u1ea1n thi\u1ebft k\u1ebf m\u1ed9t API endpoint r\u00f5 r\u00e0ng nh\u01b0 th\u1ebf n\u00e0o?", "B\u1ea1n x\u1eed l\u00fd validation v\u00e0 l\u1ed7i nh\u01b0 th\u1ebf n\u00e0o?"])
        elif normalized_skill in {"database", "sql", "postgresql", "mysql", "mongodb"}:
            questions.extend(["B\u1ea1n s\u1ebd thi\u1ebft k\u1ebf schema cho t\u00ednh n\u0103ng n\u00e0y nh\u01b0 th\u1ebf n\u00e0o?", "B\u1ea1n tr\u00e1nh query k\u00e9m hi\u1ec7u qu\u1ea3 nh\u01b0 th\u1ebf n\u00e0o?"])
        elif normalized_skill in {"react", "next.js", "typescript", "javascript"}:
            questions.extend(["B\u1ea1n qu\u1ea3n l\u00fd loading state v\u00e0 error state trong UI nh\u01b0 th\u1ebf n\u00e0o?", "Component g\u1ecdi backend API an to\u00e0n nh\u01b0 th\u1ebf n\u00e0o?"])
        elif normalized_skill in {"docker", "ci/cd"}:
            questions.extend(["V\u00ec sao n\u00ean d\u00f9ng Docker cho local development ho\u1eb7c deployment?", "B\u1ea1n s\u1ebd debug container kh\u00f4ng kh\u1edfi \u0111\u1ed9ng \u0111\u01b0\u1ee3c nh\u01b0 th\u1ebf n\u00e0o?"])
        else:
            questions.append(f"B\u1ea1n \u0111\u00e3 \u00e1p d\u1ee5ng {skill} trong project th\u1ef1c t\u1ebf nh\u01b0 th\u1ebf n\u00e0o?")
    return _dedupe(questions)[:2] or [f"B\u1ea1n \u0111\u00e3 x\u00e2y d\u1ef1ng g\u00ec \u0111\u1ec3 ch\u1ee9ng minh m\u1ee9c \u0111\u1ed9 s\u1eb5n s\u00e0ng cho {target_role}?"]


def _expected_output_for_skills(skills: list[str], target_role: str) -> str:
    return f"M\u1ed9t artifact c\u1ee5 th\u1ec3 cho {', '.join(skills)}: commit, README, demo, test case ho\u1eb7c CV bullet s\u00e1t v\u1edbi {target_role}."


def _fallback_focus(week_number: int, item_count: int, target_role: str, personalized: bool) -> str:
    if not personalized and week_number == 1:
        return f"L\u00e0m r\u00f5 y\u00eau c\u1ea7u n\u1ec1n t\u1ea3ng c\u1ee7a {target_role} v\u00ec b\u1ea1n ch\u01b0a ch\u1ecdn analysis."
    if week_number == item_count:
        return f"Ho\u00e0n thi\u1ec7n \u0111\u1ed9 kh\u1edbp c\u1ee7a CV v\u00e0 c\u00e2u chuy\u1ec7n ph\u1ecfng v\u1ea5n cho {target_role}."
    if week_number == 1:
        return f"X\u00e1c \u0111\u1ecbnh project evidence m\u1ea1nh nh\u1ea5t cho {target_role}."
    return f"C\u1ee7ng c\u1ed1 m\u1ed9t project \u0111\u1ec3 ch\u1ee9ng minh t\u1ed1t h\u01a1n m\u1ee9c \u0111\u1ed9 s\u1eb5n s\u00e0ng cho {target_role}."


def _fallback_actions(week_number: int, target_role: str) -> list[str]:
    if week_number == 1:
        return [
            f"\u0110\u1ecdc 2-3 JD th\u1ef1c t\u1ebf cho {target_role} v\u00e0 li\u1ec7t k\u00ea c\u00e1c y\u00eau c\u1ea7u l\u1eb7p l\u1ea1i.",
            "So s\u00e1nh c\u00e1c y\u00eau c\u1ea7u \u0111\u00f3 v\u1edbi CV/profile v\u00e0 ch\u1ecdn m\u1ed9t gap c\u1ea7n ch\u1ee9ng minh tr\u01b0\u1edbc.",
        ]
    return [
        "Vi\u1ebft l\u1ea1i m\u1ed9t project theo c\u1ea5u tr\u00fac: b\u00e0i to\u00e1n, tech stack, tr\u00e1ch nhi\u1ec7m c\u00e1 nh\u00e2n v\u00e0 output.",
        "Ch\u1ec9 th\u00eam keyword ph\u1ea3n \u00e1nh vi\u1ec7c b\u1ea1n \u0111\u00e3 th\u1eadt s\u1ef1 l\u00e0m, kh\u00f4ng th\u00eam k\u1ef9 n\u0103ng b\u1ea1n ch\u01b0a d\u00f9ng.",
    ]


def _fallback_practice_task(week_number: int, target_role: str) -> str:
    if week_number == 1:
        return f"T\u1ea1o checklist m\u1ed9t trang g\u1ed3m 5 y\u00eau c\u1ea7u quan tr\u1ecdng nh\u1ea5t c\u1ee7a {target_role} v\u00e0 map t\u1eebng y\u00eau c\u1ea7u v\u1edbi evidence hi\u1ec7n c\u00f3 trong CV."
    return "C\u1ea3i thi\u1ec7n m\u1ed9t artifact s\u1eb5n c\u00f3 c\u1ee7a project: README, demo flow, test case, API endpoint, UI state ho\u1eb7c ph\u1ea7n gi\u1ea3i th\u00edch notebook."


def _fallback_cv_evidence(week_number: int, target_role: str) -> str:
    if week_number == 1:
        return "Ch\u01b0a th\u00eam claim m\u1edbi v\u00e0o CV. H\u00e3y t\u1ea1o checklist gap v\u00e0 x\u00e1c \u0111\u1ecbnh project hi\u1ec7n c\u00f3 n\u00e0o c\u00f3 th\u1ec3 h\u1ed7 tr\u1ee3 vai tr\u00f2 m\u1ee5c ti\u00eau."
    return f"N\u1ebfu evidence project \u0111\u00e3 c\u1ea3i thi\u1ec7n l\u00e0 th\u1eadt, h\u00e3y th\u00eam m\u1ed9t CV bullet ng\u1eafn g\u1ecdn s\u00e1t v\u1edbi {target_role}. Kh\u00f4ng t\u1ef1 b\u1ecba metric."


def _fallback_interview_questions(target_role: str) -> list[str]:
    return [
        f"Project n\u00e0o ch\u1ee9ng minh t\u1ed1t nh\u1ea5t m\u1ee9c \u0111\u1ed9 ph\u00f9 h\u1ee3p c\u1ee7a b\u1ea1n v\u1edbi {target_role}?",
        "B\u1ea1n c\u00f3 th\u1ec3 gi\u1ea3i th\u00edch r\u00f5 tradeoff k\u1ef9 thu\u1eadt ho\u1eb7c bug n\u00e0o t\u1eeb project \u0111\u00f3?",
    ]



def _fallback_expected_output(week_number: int, item_count: int, target_role: str) -> str:
    if week_number == item_count:
        return f"Ph\u1ea7n CV/profile \u0111\u00e3 c\u1eadp nh\u1eadt v\u00e0 m\u1ed9t c\u00e2u chuy\u1ec7n ph\u1ecfng v\u1ea5n ng\u1eafn cho {target_role}."
    return "M\u1ed9t artifact project ho\u1eb7c experience bullet \u0111\u00e3 \u0111\u01b0\u1ee3c c\u1ea3i thi\u1ec7n, r\u00f5 h\u01a1n, an to\u00e0n h\u01a1n v\u00e0 s\u00e1t JD m\u1ee5c ti\u00eau h\u01a1n."

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
    return normalize_skill_list(_dedupe(skills))[:10]


def _fallback_growth_skills(roles: list[str], current_skills: set[str]) -> list[str]:
    candidates = _core_skills_for_roles(roles)
    return [skill for skill in candidates if skill not in current_skills][:6]


def _generic_skill_action(skill: str) -> str:
    normalized_skill = skill.lower()
    if normalized_skill in {"docker", "git", "github", "ci/cd"}:
        return f"\u00c1p d\u1ee5ng {skill} theo c\u00e1ch th\u1ef1c t\u1ebf: setup, l\u1ec7nh ch\u1ea1y local, l\u1ed7i th\u01b0\u1eddng g\u1eb7p v\u00e0 ghi ch\u00fa README."
    if normalized_skill in {"rest api", "api", "fastapi", "django", "flask", "node.js", "express", "asp.net core"}:
        return f"X\u00e2y d\u1ef1ng m\u1ed9t flow {skill} nh\u1ecf: CRUD, validation, error handling v\u00e0 t\u00e0i li\u1ec7u endpoint."
    if normalized_skill in {"postgresql", "mysql", "mongodb", "sql", "database"}:
        return f"T\u1ea1o v\u00ed d\u1ee5 database cho {skill}: schema, query ch\u00ednh v\u00e0 t\u00edch h\u1ee3p v\u00e0o t\u00ednh n\u0103ng."
    if normalized_skill in {"authentication", "jwt", "oauth"}:
        return f"Tri\u1ec3n khai auth flow nh\u1ecf v\u1edbi {skill}: login, protected route v\u00e0 l\u1ed7i permission th\u01b0\u1eddng g\u1eb7p."
    if normalized_skill in {"react", "next.js", "typescript", "javascript", "tailwind", "html", "css"}:
        return f"T\u1ea1o ho\u1eb7c c\u1ea3i thi\u1ec7n m\u1ed9t UI nh\u1ecf v\u1edbi {skill}: form, state, t\u00edch h\u1ee3p API v\u00e0 layout responsive."
    if normalized_skill in {"ai", "machine learning", "nlp", "scikit-learn", "pytorch", "tensorflow"}:
        return f"X\u00e2y d\u1ef1ng m\u1ed9t notebook/project {skill} nh\u1ecf: d\u1eef li\u1ec7u \u0111\u1ea7u v\u00e0o, metric \u0111\u01a1n gi\u1ea3n v\u00e0 k\u1ebft qu\u1ea3 d\u1ec5 gi\u1ea3i th\u00edch."
    return f"H\u1ecdc {skill} th\u00f4ng qua output c\u1ee5 th\u1ec3: ghi ch\u00fa, lab, commit ho\u1eb7c artifact project."


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
        return "\u0111\u1ed9 kh\u1edbp CV v\u00e0 \u0111\u1ed9 r\u00f5 c\u1ee7a evidence v\u00ec ch\u01b0a ph\u00e1t hi\u1ec7n skill gap l\u1edbn"
    if high:
        return f"{total} skill gap, \u01b0u ti\u00ean cao nh\u1ea5t l\u00e0 {', '.join(high[:3])}"
    if medium:
        return f"{total} skill gap, t\u1eadp trung v\u00e0o k\u1ef9 n\u0103ng \u01b0u ti\u00ean trung b\u00ecnh: {', '.join(medium[:4])}"
    return f"{total} gap \u01b0u ti\u00ean th\u1ea5p \u0111\u1ec3 c\u1ea3i thi\u1ec7n \u0111\u1ed9 kh\u1edbp CV: {', '.join(low[:4])}"


def _dedupe(items: list[str]) -> list[str]:
    result = []
    seen = set()
    for item in items:
        normalized = item.strip()
        if normalized and normalized not in seen:
            result.append(normalized)
            seen.add(normalized)
    return result
