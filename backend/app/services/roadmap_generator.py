import re

from app.models.career_profile import CareerProfile
from app.services.resume_job_matcher import ROLE_CORE_SKILLS, extract_skills

DEFAULT_TARGET_ROLE = "vai trò công nghệ mục tiêu"


def infer_week_count(timeline: str | None) -> int:
    normalized = (timeline or "").strip().lower()
    week_match = re.search(r"(\d+)\s*(tuần|tuan|week|weeks)", normalized)
    if week_match:
        return max(1, int(week_match.group(1)))

    month_match = re.search(r"(\d+)\s*(tháng|thang|month|months)", normalized)
    if month_match:
        return max(1, int(month_match.group(1)) * 4)

    return 6

def build_roadmap_from_analysis(
    *,
    target_role: str,
    current_level: str,
    timeline: str,
    prioritized_missing_skills: dict[str, list[str]],
    improvement_plan: list[str],
) -> dict[str, object]:
    week_count = infer_week_count(timeline)
    target_role = target_role.strip() or DEFAULT_TARGET_ROLE
    current_level = current_level.strip() or "chưa xác định"
    high = prioritized_missing_skills.get("high_priority", [])
    medium = prioritized_missing_skills.get("medium_priority", [])
    low = prioritized_missing_skills.get("low_priority", [])
    skill_queue = _dedupe(high + medium + low)

    items = _build_items(
        week_count=week_count,
        target_role=target_role,
        current_level=current_level,
        skill_queue=skill_queue,
        high_priority=set(high),
        improvement_plan=improvement_plan,
    )
    gap_text = _gap_summary(high, medium, low)
    return {
        "title": f"Roadmap {week_count} tuần cho {target_role}",
        "target_role": target_role,
        "timeline": timeline or f"{week_count} tuần",
        "items": items,
        "summary": f"Roadmap tập trung vào {gap_text}. Mục tiêu là tạo bằng chứng năng lực rõ ràng hơn cho {target_role}, dựa trên skill gap từ phân tích CV và Job Description gần nhất.",
    }


def build_roadmap_from_profile(profile: CareerProfile, timeline: str | None = None) -> dict[str, object]:
    selected_timeline = (timeline or profile.timeline or "").strip()
    week_count = infer_week_count(selected_timeline)
    target_role = profile.target_role.strip() or DEFAULT_TARGET_ROLE
    current_level = profile.current_level.strip() or "chưa xác định"
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
            "Rà soát lại CV/profile để mô tả rõ project, vai trò cá nhân, tech stack và kết quả đạt được.",
            "Chọn một project gần với target role và viết lại thành case study ngắn có input, xử lý, output và impact.",
        ]

    items = _build_items(
        week_count=week_count,
        target_role=target_role,
        current_level=current_level,
        skill_queue=missing_skills,
        high_priority=high_priority,
        improvement_plan=improvement_plan,
    )
    return {
        "title": f"Roadmap {week_count} tuần cho {target_role}",
        "target_role": target_role,
        "timeline": selected_timeline or f"{week_count} tuần",
        "items": items,
        "summary": f"Roadmap basic được tạo từ career profile hiện có. Trọng tâm là đưa người dùng từ level {current_level} tiến gần hơn tới {target_role} bằng các bước học và bằng chứng project ngắn hạn.",
    }


def _build_items(
    *,
    week_count: int,
    target_role: str,
    current_level: str,
    skill_queue: list[str],
    high_priority: set[str],
    improvement_plan: list[str],
) -> list[dict[str, object]]:
    items = []
    clean_skills = skill_queue or []
    actions = improvement_plan or []

    for index in range(week_count):
        week_number = index + 1
        focus_skills = _skills_for_week(clean_skills, index, week_count)
        if focus_skills:
            focus = _focus_for_skills(focus_skills, high_priority)
            item_actions = _actions_for_week(focus_skills, actions, target_role, current_level)
            expected_output = _expected_output_for_skills(focus_skills, target_role)
        else:
            focus = _fallback_focus(week_number, week_count, target_role)
            item_actions = _fallback_actions(week_number, target_role)
            expected_output = _fallback_expected_output(week_number, week_count, target_role)

        items.append(
            {
                "week": f"Tuần {week_number}",
                "focus": focus,
                "skills": focus_skills,
                "actions": item_actions,
                "expected_output": expected_output,
            }
        )

    return items


def _skills_for_week(skills: list[str], index: int, week_count: int) -> list[str]:
    if not skills:
        return []
    if len(skills) <= week_count:
        return [skills[index]] if index < len(skills) else []
    chunk_size = max(1, (len(skills) + week_count - 1) // week_count)
    start = index * chunk_size
    return skills[start : start + chunk_size]


def _focus_for_skills(skills: list[str], high_priority: set[str]) -> str:
    if any(skill in high_priority for skill in skills):
        return f"Xử lý skill gap ưu tiên cao: {', '.join(skills)}"
    return f"Củng cố kỹ năng còn thiếu: {', '.join(skills)}"


def _actions_for_week(skills: list[str], improvement_plan: list[str], target_role: str, current_level: str) -> list[str]:
    selected_actions = []
    for skill in skills:
        matching_action = next((action for action in improvement_plan if skill.lower() in action.lower()), None)
        selected_actions.append(matching_action or _generic_skill_action(skill))

    selected_actions.append(
        f"Tạo một mini task hoặc update project hiện có để chứng minh kỹ năng này theo hướng {target_role}."
    )
    if current_level.lower() in {"fresher", "junior", "beginner", "entry level"}:
        selected_actions.append("Ghi lại phần đã học bằng README ngắn: vấn đề, cách làm, lỗi gặp phải và kết quả.")
    return _dedupe(selected_actions)[:4]


def _expected_output_for_skills(skills: list[str], target_role: str) -> str:
    return f"Có bằng chứng thực tế cho {', '.join(skills)}: commit, README, demo nhỏ hoặc đoạn mô tả CV phù hợp với {target_role}."


def _fallback_focus(week_number: int, week_count: int, target_role: str) -> str:
    if week_number == week_count:
        return f"Hoàn thiện CV alignment và chuẩn bị apply cho {target_role}"
    if week_number == 1:
        return f"Làm rõ yêu cầu nền tảng của {target_role}"
    return f"Củng cố project gần nhất với {target_role}"


def _fallback_actions(week_number: int, target_role: str) -> list[str]:
    if week_number == 1:
        return [
            f"Đọc lại 2-3 JD thật cho {target_role} và ghi ra skill xuất hiện lặp lại.",
            "So sánh skill đó với CV/profile hiện tại để chọn phần cần làm rõ trước.",
        ]
    return [
        "Viết lại một project theo cấu trúc: vấn đề, tech stack, vai trò cá nhân, kết quả.",
        "Bổ sung keyword đúng năng lực thật vào CV thay vì liệt kê lan man.",
    ]


def _fallback_expected_output(week_number: int, week_count: int, target_role: str) -> str:
    if week_number == week_count:
        return f"Có bản CV/profile cập nhật và checklist apply thử cho {target_role}."
    return "Có một phần project hoặc experience được viết lại rõ hơn, sát với JD mục tiêu."


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
        return f"Học và áp dụng {skill} ở mức thực dụng: setup, chạy local, ghi lại command và lỗi thường gặp."
    if skill in {"rest api", "api", "fastapi", "django", "flask", "node.js", "express"}:
        return f"Xây một flow API nhỏ với {skill}: CRUD, validation, error handling và tài liệu endpoint."
    if skill in {"postgresql", "mysql", "mongodb", "sql", "database"}:
        return f"Tạo ví dụ database cho {skill}: schema, query chính và cách dữ liệu liên kết với feature."
    if skill in {"authentication", "jwt", "oauth"}:
        return f"Làm rõ token/auth flow với {skill}: login, protected route và lỗi quyền truy cập phổ biến."
    if skill in {"react", "next.js", "typescript", "javascript", "tailwind", "html", "css"}:
        return f"Tạo hoặc cải thiện UI nhỏ bằng {skill}: form, state, API integration và responsive layout."
    if skill in {"ai", "machine learning", "nlp", "scikit-learn", "pytorch", "tensorflow"}:
        return f"Làm mini notebook/project về {skill}: dữ liệu đầu vào, metric đơn giản và kết quả giải thích được."
    return f"Học {skill} theo hướng có output: note ngắn, bài lab nhỏ hoặc commit vào project thật."


def _gap_summary(high: list[str], medium: list[str], low: list[str]) -> str:
    total = len(high) + len(medium) + len(low)
    if total == 0:
        return "CV alignment và cách trình bày năng lực vì chưa phát hiện skill gap lớn"
    if high:
        return f"{total} skill gap, ưu tiên cao nhất là {', '.join(high[:3])}"
    if medium:
        return f"{total} skill gap, trọng tâm là nhóm ưu tiên trung bình: {', '.join(medium[:4])}"
    return f"{total} skill gap ưu tiên thấp, chủ yếu dùng để tinh chỉnh CV: {', '.join(low[:4])}"


def _dedupe(items: list[str]) -> list[str]:
    result = []
    seen = set()
    for item in items:
        normalized = item.strip()
        if normalized and normalized not in seen:
            result.append(normalized)
            seen.add(normalized)
    return result