import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "docs" / "datasets" / "synthetic"
OUTPUT_FILE = OUTPUT_DIR / "synthetic_cases.json"


ROLE_TEMPLATES: dict[str, dict[str, Any]] = {
    "backend_dotnet": {
        "target_role": "Backend .NET Intern",
        "role_family": "backend",
        "candidate_stack": ".NET, C#, SQL",
        "jd_stack": "ASP.NET Core, C#, PostgreSQL, JWT, REST API",
        "core": ["C#", "ASP.NET Core", "REST API", "JWT", "PostgreSQL"],
        "adjacent": ["Docker", "Git", "Unit Testing"],
    },
    "backend_node": {
        "target_role": "Backend Node.js Developer",
        "role_family": "backend",
        "candidate_stack": "Node.js, Express, MongoDB",
        "jd_stack": "Node.js, Express, PostgreSQL, JWT, REST API",
        "core": ["Node.js", "Express", "REST API", "JWT", "PostgreSQL"],
        "adjacent": ["Docker", "Git", "Testing"],
    },
    "backend_fastapi": {
        "target_role": "Backend Python/FastAPI Intern",
        "role_family": "backend",
        "candidate_stack": "Python, FastAPI, SQL",
        "jd_stack": "Python, FastAPI, PostgreSQL, Docker, REST API",
        "core": ["Python", "FastAPI", "REST API", "PostgreSQL", "Docker"],
        "adjacent": ["JWT", "Git", "SQLAlchemy"],
    },
    "frontend_react": {
        "target_role": "Frontend React Intern",
        "role_family": "frontend",
        "candidate_stack": "React, TypeScript, Tailwind",
        "jd_stack": "React, Next.js, TypeScript, REST API, Tailwind",
        "core": ["React", "TypeScript", "Next.js", "REST API", "Tailwind"],
        "adjacent": ["HTML", "CSS", "State Management"],
    },
    "ai_ml": {
        "target_role": "AI / Machine Learning Intern",
        "role_family": "ai/data",
        "candidate_stack": "Python, scikit-learn, pandas",
        "jd_stack": "Python, Machine Learning, scikit-learn, pandas, model evaluation",
        "core": ["Python", "Machine Learning", "scikit-learn", "pandas", "model evaluation"],
        "adjacent": ["NLP", "NumPy", "data preprocessing"],
    },
    "mobile_flutter": {
        "target_role": "Mobile Flutter Intern",
        "role_family": "mobile",
        "candidate_stack": "Flutter, Dart, Firebase",
        "jd_stack": "Flutter, Dart, Firebase, REST API, mobile UI",
        "core": ["Flutter", "Dart", "Firebase", "REST API", "mobile UI"],
        "adjacent": ["Git", "State Management", "Authentication"],
    },
    "data_analyst": {
        "target_role": "Data Analyst Intern",
        "role_family": "ai/data",
        "candidate_stack": "SQL, Excel, Power BI",
        "jd_stack": "SQL, dashboard, data cleaning, business analysis",
        "core": ["SQL", "dashboard", "data cleaning", "Power BI", "business analysis"],
        "adjacent": ["Python", "statistics", "reporting"],
    },
}


GROUPS = [
    "exact_fit",
    "same_role_different_stack",
    "role_mismatch",
    "cross_domain_transferable",
    "weak_cv",
    "keyword_stuffing",
    "non_it_mismatch",
]


def generate_cases() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for group in GROUPS:
        for index in range(10):
            cases.append(_build_case(group, index))
    return cases


def _build_case(group: str, index: int) -> dict[str, Any]:
    template_keys = list(ROLE_TEMPLATES)
    target_key = template_keys[index % len(template_keys)]
    source_key = _source_key_for_group(group, target_key, index)
    target = ROLE_TEMPLATES[target_key]
    source = ROLE_TEMPLATES[source_key]
    case_number = len(GROUPS) * index + GROUPS.index(group) + 1
    case_id = f"SYN{case_number:03d}"
    fit_label, score_range = _fit_label_and_range(group)
    overlap = _skill_overlap_for_group(group, source, target)
    missing = [skill for skill in target["core"] if skill not in overlap]

    return {
        "case_id": case_id,
        "dataset_type": "synthetic",
        "group": group,
        "candidate_profile": _candidate_profile(group, source, index),
        "resume_summary": _resume_summary(group, source, overlap, index),
        "job_description_summary": _jd_summary(target, index),
        "target_role": target["target_role"],
        "role_family": target["role_family"],
        "candidate_stack": source["candidate_stack"],
        "jd_stack": target["jd_stack"],
        "fit_label": fit_label,
        "expected_score_range": score_range,
        "reason": _reason(group, source, target, missing),
        "skill_overlap": overlap,
        "missing_critical_skills": missing,
    }


def _source_key_for_group(group: str, target_key: str, index: int) -> str:
    if group in {"exact_fit", "weak_cv", "keyword_stuffing"}:
        return target_key
    if group == "same_role_different_stack":
        backend_cycle = ["backend_dotnet", "backend_node", "backend_fastapi"]
        if target_key.startswith("backend"):
            return backend_cycle[(backend_cycle.index(target_key) + 1) % len(backend_cycle)]
        return target_key
    if group == "role_mismatch":
        mismatch = {
            "backend_dotnet": "frontend_react",
            "backend_node": "frontend_react",
            "backend_fastapi": "frontend_react",
            "frontend_react": "backend_dotnet",
            "ai_ml": "mobile_flutter",
            "mobile_flutter": "ai_ml",
            "data_analyst": "backend_node",
        }
        return mismatch.get(target_key, "frontend_react")
    if group == "cross_domain_transferable":
        transfer = {
            "backend_dotnet": "data_analyst",
            "backend_node": "data_analyst",
            "backend_fastapi": "ai_ml",
            "frontend_react": "mobile_flutter",
            "ai_ml": "backend_fastapi",
            "mobile_flutter": "frontend_react",
            "data_analyst": "ai_ml",
        }
        return transfer.get(target_key, "data_analyst")
    if group == "non_it_mismatch":
        return "data_analyst" if index % 2 else "frontend_react"
    return target_key


def _fit_label_and_range(group: str) -> tuple[str, str]:
    mapping = {
        "exact_fit": ("good", "75-90"),
        "same_role_different_stack": ("medium", "50-70"),
        "role_mismatch": ("mismatch", "25-50"),
        "cross_domain_transferable": ("medium", "35-60"),
        "weak_cv": ("weak", "35-55"),
        "keyword_stuffing": ("weak", "20-45"),
        "non_it_mismatch": ("mismatch", "10-35"),
    }
    return mapping[group]


def _skill_overlap_for_group(group: str, source: dict[str, Any], target: dict[str, Any]) -> list[str]:
    if group == "exact_fit":
        return list(target["core"][:4])
    if group == "same_role_different_stack":
        return [skill for skill in ["REST API", "JWT", "PostgreSQL", "Docker", "Git"] if skill in target["core"] + target["adjacent"]]
    if group == "role_mismatch":
        return [skill for skill in ["REST API", "Git", "Authentication"] if skill in target["core"] + target["adjacent"]]
    if group == "cross_domain_transferable":
        return [skill for skill in source["core"] + source["adjacent"] if skill in target["core"] + target["adjacent"]][:3]
    if group == "weak_cv":
        return list(target["core"][:2])
    if group == "keyword_stuffing":
        return list(target["core"][:3])
    if group == "non_it_mismatch":
        return []
    return []


def _candidate_profile(group: str, source: dict[str, Any], index: int) -> str:
    if group == "non_it_mismatch":
        return f"Ứng viên chuyển ngành từ marketing/business, có quan tâm công nghệ nhưng chưa có project kỹ thuật rõ ràng #{index + 1}."
    if group == "keyword_stuffing":
        return f"Ứng viên liệt kê nhiều keyword thuộc {source['candidate_stack']} nhưng mô tả project còn rất mỏng #{index + 1}."
    if group == "weak_cv":
        return f"Ứng viên junior có nền tảng {source['candidate_stack']} nhưng CV thiếu chi tiết về trách nhiệm và output #{index + 1}."
    return f"Ứng viên có kinh nghiệm học tập/project với {source['candidate_stack']} #{index + 1}."


def _resume_summary(group: str, source: dict[str, Any], overlap: list[str], index: int) -> str:
    if group == "non_it_mismatch":
        return "CV tập trung vào marketing, teamwork và phân tích khách hàng; chưa có evidence về lập trình, API, database hoặc deployment."
    if group == "keyword_stuffing":
        return f"CV có danh sách keyword {', '.join(overlap)} nhưng không mô tả project, nhiệm vụ kỹ thuật hoặc kết quả cụ thể."
    if group == "weak_cv":
        return f"CV nhắc đến {', '.join(overlap)} nhưng phần project chỉ ghi chung chung như built an app hoặc worked on system."
    return f"CV mô tả project dùng {', '.join(overlap or source['core'][:2])}, có một phần kinh nghiệm thực hành và một số evidence kỹ thuật."


def _jd_summary(target: dict[str, Any], index: int) -> str:
    return (
        f"JD synthetic cho {target['target_role']} yêu cầu {', '.join(target['core'])}; "
        f"ưu tiên ứng viên có project thực tế, hiểu tradeoff cơ bản và có khả năng trình bày evidence kỹ thuật #{index + 1}."
    )


def _reason(group: str, source: dict[str, Any], target: dict[str, Any], missing: list[str]) -> str:
    if group == "exact_fit":
        return "Ứng viên và JD cùng role/stack chính, còn thiếu một vài kỹ năng phụ nên không nên chấm tuyệt đối."
    if group == "same_role_different_stack":
        return "Cùng role family nhưng khác stack chính; nên có điểm trung bình khá và giải thích rõ stack gap."
    if group == "role_mismatch":
        return "Role family khác nhau nên cần penalty rõ dù vẫn có một ít keyword kỹ thuật chung."
    if group == "cross_domain_transferable":
        return "Có một số transferable skills nhưng chưa đủ evidence cho target role chính."
    if group == "weak_cv":
        return "Role có vẻ phù hợp nhưng CV thiếu evidence project/experience nên confidence thấp hơn."
    if group == "keyword_stuffing":
        return "CV chứa keyword liên quan nhưng thiếu evidence meaningful usage; matcher không nên over-score."
    if group == "non_it_mismatch":
        return "Profile không có evidence kỹ thuật phù hợp với JD công nghệ; điểm nên thấp và confidence thấp."
    return f"Thiếu kỹ năng trọng yếu: {', '.join(missing)}."


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "careeros-synthetic-dataset-v1",
        "dataset_type": "synthetic",
        "description": "Synthetic CV/JD matching cases tự tạo, không chứa CV thật, JD thật hoặc PII.",
        "case_count": 70,
        "cases": generate_cases(),
    }
    OUTPUT_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Generated {len(payload['cases'])} synthetic cases at {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
