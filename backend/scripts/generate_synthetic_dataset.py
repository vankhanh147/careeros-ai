import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "docs" / "datasets" / "synthetic"
OUTPUT_FILE = OUTPUT_DIR / "synthetic_cases.json"
STATISTICS_FILE = OUTPUT_DIR / "STATISTICS.md"
CASE_COUNT_PER_CATEGORY = 30


SENIORITIES = ["Intern", "Fresher", "Junior", "Mid-level"]

ROLE_TEMPLATES: list[dict[str, Any]] = [
    {
        "role_key": "backend_dotnet",
        "target_role": "Backend Developer",
        "role_family": "backend",
        "candidate_stack": ".NET, C#, SQL",
        "jd_stack": "ASP.NET Core, C#, PostgreSQL, JWT, REST API",
        "core": ["C#", "ASP.NET Core", "REST API", "JWT", "PostgreSQL"],
        "adjacent": ["Docker", "Git", "Unit Testing", "CI/CD"],
    },
    {
        "role_key": "frontend_react",
        "target_role": "Frontend Developer",
        "role_family": "frontend",
        "candidate_stack": "React, TypeScript, Tailwind",
        "jd_stack": "React, Next.js, TypeScript, REST API, Tailwind",
        "core": ["React", "TypeScript", "Next.js", "REST API", "Tailwind"],
        "adjacent": ["HTML", "CSS", "State Management", "Testing"],
    },
    {
        "role_key": "fullstack",
        "target_role": "Fullstack Developer",
        "role_family": "fullstack",
        "candidate_stack": "React, Node.js, PostgreSQL",
        "jd_stack": "React, Node.js, REST API, PostgreSQL, Authentication",
        "core": ["React", "Node.js", "REST API", "PostgreSQL", "Authentication"],
        "adjacent": ["TypeScript", "Docker", "Git", "CI/CD"],
    },
    {
        "role_key": "mobile_flutter",
        "target_role": "Mobile Developer",
        "role_family": "mobile",
        "candidate_stack": "Flutter, Dart, Firebase",
        "jd_stack": "Flutter, Dart, Firebase, REST API, mobile UI",
        "core": ["Flutter", "Dart", "Firebase", "REST API", "mobile UI"],
        "adjacent": ["Git", "State Management", "Authentication", "Testing"],
    },
    {
        "role_key": "ai_engineer",
        "target_role": "AI Engineer",
        "role_family": "ai/data",
        "candidate_stack": "Python, NLP, Sentence Transformers",
        "jd_stack": "Python, NLP, embeddings, model evaluation, API integration",
        "core": ["Python", "NLP", "embeddings", "model evaluation", "API integration"],
        "adjacent": ["Machine Learning", "scikit-learn", "FastAPI", "data preprocessing"],
    },
    {
        "role_key": "ml_engineer",
        "target_role": "Machine Learning Engineer",
        "role_family": "ai/data",
        "candidate_stack": "Python, scikit-learn, pandas",
        "jd_stack": "Python, Machine Learning, scikit-learn, pandas, model evaluation",
        "core": ["Python", "Machine Learning", "scikit-learn", "pandas", "model evaluation"],
        "adjacent": ["NumPy", "data preprocessing", "feature engineering", "ML pipeline"],
    },
    {
        "role_key": "data_analyst",
        "target_role": "Data Analyst",
        "role_family": "ai/data",
        "candidate_stack": "SQL, Excel, Power BI",
        "jd_stack": "SQL, dashboard, data cleaning, business analysis, reporting",
        "core": ["SQL", "dashboard", "data cleaning", "Power BI", "business analysis"],
        "adjacent": ["Python", "statistics", "reporting", "Excel"],
    },
    {
        "role_key": "data_engineer",
        "target_role": "Data Engineer",
        "role_family": "ai/data",
        "candidate_stack": "Python, SQL, ETL",
        "jd_stack": "Python, SQL, ETL, data pipeline, warehouse",
        "core": ["Python", "SQL", "ETL", "data pipeline", "warehouse"],
        "adjacent": ["Airflow", "Docker", "PostgreSQL", "data quality"],
    },
    {
        "role_key": "devops",
        "target_role": "DevOps Engineer",
        "role_family": "devops",
        "candidate_stack": "Docker, CI/CD, cloud",
        "jd_stack": "Docker, CI/CD, deployment, monitoring, Linux",
        "core": ["Docker", "CI/CD", "deployment", "monitoring", "Linux"],
        "adjacent": ["GitHub Actions", "cloud", "logging", "networking"],
    },
    {
        "role_key": "qa",
        "target_role": "QA Engineer",
        "role_family": "qa/testing",
        "candidate_stack": "Manual testing, API testing, SQL",
        "jd_stack": "test case, API testing, regression testing, SQL, bug report",
        "core": ["test case", "API testing", "regression testing", "SQL", "bug report"],
        "adjacent": ["automation testing", "Postman", "Git", "Agile"],
    },
    {
        "role_key": "cybersecurity",
        "target_role": "Cybersecurity Analyst",
        "role_family": "cybersecurity",
        "candidate_stack": "network security, Linux, incident response",
        "jd_stack": "security monitoring, vulnerability assessment, Linux, network security, incident response",
        "core": ["security monitoring", "vulnerability assessment", "Linux", "network security", "incident response"],
        "adjacent": ["OWASP", "SIEM", "Python", "risk assessment"],
    },
]

CATEGORIES = [
    "exact_fit",
    "strong_evidence",
    "same_role_different_stack",
    "role_mismatch",
    "cross_domain_transferable",
    "weak_cv",
    "keyword_stuffing",
    "non_it_mismatch",
    "career_switch",
    "missing_critical_skill",
]

CAREER_SWITCH_SOURCES = [
    "Marketing",
    "Sales",
    "Mechanical Engineer",
    "Accounting",
    "Customer Support",
    "Teacher",
]


CATEGORY_LABELS = {
    "exact_fit": ("good", "75-90"),
    "strong_evidence": ("good", "82-95"),
    "same_role_different_stack": ("medium", "50-70"),
    "role_mismatch": ("mismatch", "25-50"),
    "cross_domain_transferable": ("medium", "35-60"),
    "weak_cv": ("weak", "35-55"),
    "keyword_stuffing": ("weak", "20-45"),
    "non_it_mismatch": ("mismatch", "10-35"),
    "career_switch": ("mismatch", "15-40"),
    "missing_critical_skill": ("weak", "40-60"),
}


def generate_cases() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    case_number = 1
    for category in CATEGORIES:
        for index in range(CASE_COUNT_PER_CATEGORY):
            cases.append(_build_case(case_number, category, index))
            case_number += 1
    return cases


def _build_case(case_number: int, category: str, index: int) -> dict[str, Any]:
    target = ROLE_TEMPLATES[(case_number - 1) % len(ROLE_TEMPLATES)]
    source = _source_for_category(category, target, index)
    seniority = SENIORITIES[(index + CATEGORIES.index(category)) % len(SENIORITIES)]
    fit_label, score_range = CATEGORY_LABELS[category]
    overlap = _skill_overlap_for_category(category, source, target)
    missing = [skill for skill in target["core"] if skill not in overlap]
    career_switch_source = CAREER_SWITCH_SOURCES[index % len(CAREER_SWITCH_SOURCES)]

    return {
        "case_id": f"SYN{case_number:03d}",
        "dataset_type": "synthetic",
        "category": category,
        "group": category,
        "seniority": seniority,
        "candidate_profile": _candidate_profile(category, source, seniority, index, career_switch_source),
        "resume_summary": _resume_summary(category, source, overlap, seniority, career_switch_source),
        "job_description_summary": _jd_summary(target, seniority, index),
        "target_role": target["target_role"],
        "role_family": target["role_family"],
        "candidate_stack": _candidate_stack(category, source, career_switch_source),
        "jd_stack": target["jd_stack"],
        "fit_label": fit_label,
        "expected_score_range": score_range,
        "reason": _reason(category, source, target, missing, seniority, career_switch_source),
        "skill_overlap": overlap,
        "missing_critical_skills": missing,
    }


def _source_for_category(category: str, target: dict[str, Any], index: int) -> dict[str, Any]:
    if category in {"exact_fit", "strong_evidence", "weak_cv", "keyword_stuffing", "missing_critical_skill"}:
        return target
    if category == "same_role_different_stack":
        same_family = [role for role in ROLE_TEMPLATES if role["role_family"] == target["role_family"] and role["role_key"] != target["role_key"]]
        return same_family[index % len(same_family)] if same_family else target
    if category == "role_mismatch":
        mismatch_roles = [role for role in ROLE_TEMPLATES if role["role_family"] != target["role_family"]]
        return mismatch_roles[(index + 3) % len(mismatch_roles)]
    if category == "cross_domain_transferable":
        transferable = [role for role in ROLE_TEMPLATES if role["role_family"] != target["role_family"]]
        return transferable[(index + 5) % len(transferable)]
    if category in {"non_it_mismatch", "career_switch"}:
        return target
    return target


def _skill_overlap_for_category(category: str, source: dict[str, Any], target: dict[str, Any]) -> list[str]:
    if category == "exact_fit":
        return list(target["core"][:4])
    if category == "strong_evidence":
        return list(target["core"] + target["adjacent"][:2])
    if category == "same_role_different_stack":
        overlap = [skill for skill in source["core"] + source["adjacent"] if skill in target["core"] + target["adjacent"]]
        return overlap[:3] or [target["core"][0]]
    if category == "role_mismatch":
        return [skill for skill in ["REST API", "Git", "SQL", "Python", "Linux"] if skill in target["core"] + target["adjacent"]]
    if category == "cross_domain_transferable":
        overlap = [skill for skill in source["core"] + source["adjacent"] if skill in target["core"] + target["adjacent"]]
        return overlap[:3]
    if category == "weak_cv":
        return list(target["core"][:2])
    if category == "keyword_stuffing":
        return list(target["core"][:3])
    if category == "missing_critical_skill":
        return list(target["core"][1:4])
    return []


def _candidate_stack(category: str, source: dict[str, Any], career_switch_source: str) -> str:
    if category == "career_switch":
        return f"{career_switch_source}, transferable soft skills"
    if category == "non_it_mismatch":
        return "Business, communication, operations"
    return source["candidate_stack"]


def _candidate_profile(category: str, source: dict[str, Any], seniority: str, index: int, career_switch_source: str) -> str:
    if category == "career_switch":
        return f"Ứng viên {seniority} chuyển ngành từ {career_switch_source}, mới học nền tảng công nghệ và chưa có nhiều project production #{index + 1}."
    if category == "non_it_mismatch":
        return f"Ứng viên {seniority} có nền tảng business/operations, quan tâm công nghệ nhưng chưa có project kỹ thuật rõ #{index + 1}."
    if category == "keyword_stuffing":
        return f"Ứng viên {seniority} liệt kê nhiều keyword thuộc {source['candidate_stack']} nhưng mô tả project còn mỏng #{index + 1}."
    if category == "strong_evidence":
        return f"Ứng viên {seniority} có nhiều project, từng deploy thật và mô tả trách nhiệm kỹ thuật rõ với {source['candidate_stack']} #{index + 1}."
    if category == "weak_cv":
        return f"Ứng viên {seniority} có nền tảng {source['candidate_stack']} nhưng CV thiếu chi tiết về project, trách nhiệm và output #{index + 1}."
    return f"Ứng viên {seniority} có kinh nghiệm học tập hoặc project với {source['candidate_stack']} #{index + 1}."


def _resume_summary(category: str, source: dict[str, Any], overlap: list[str], seniority: str, career_switch_source: str) -> str:
    if category == "career_switch":
        return f"CV nhấn mạnh kinh nghiệm {career_switch_source}, kỹ năng giao tiếp và tự học; mới có bài tập nhỏ, chưa có evidence mạnh cho role kỹ thuật."
    if category == "non_it_mismatch":
        return "CV tập trung vào business, teamwork và vận hành; chưa có evidence về lập trình, API, database, testing hoặc deployment."
    if category == "keyword_stuffing":
        return f"CV có danh sách keyword {', '.join(overlap)} nhưng không mô tả project, nhiệm vụ kỹ thuật hoặc kết quả cụ thể."
    if category == "weak_cv":
        return f"CV nhắc đến {', '.join(overlap)} nhưng project chỉ ghi chung chung, thiếu bối cảnh, thiếu trách nhiệm và thiếu output kiểm chứng."
    if category == "strong_evidence":
        return f"CV mô tả nhiều project dùng {', '.join(overlap)}, có deploy thật, CI/CD hoặc trải nghiệm production phù hợp mức {seniority}."
    if category == "missing_critical_skill":
        return f"CV có evidence với {', '.join(overlap)} nhưng thiếu một số kỹ năng critical của JD, cần bổ sung project hoặc học thêm."
    return f"CV mô tả project dùng {', '.join(overlap or source['core'][:2])}, có một phần kinh nghiệm thực hành và evidence kỹ thuật cơ bản."


def _jd_summary(target: dict[str, Any], seniority: str, index: int) -> str:
    return (
        f"JD synthetic cho {target['target_role']} mức {seniority} yêu cầu {', '.join(target['core'])}; "
        f"ưu tiên ứng viên có project thực tế, hiểu tradeoff cơ bản và trình bày evidence kỹ thuật #{index + 1}."
    )


def _reason(category: str, source: dict[str, Any], target: dict[str, Any], missing: list[str], seniority: str, career_switch_source: str) -> str:
    if category == "exact_fit":
        return "Ứng viên và JD cùng role/stack chính, có overlap mạnh nhưng vẫn thiếu một vài kỹ năng phụ nên không nên chấm tuyệt đối."
    if category == "strong_evidence":
        return "Ứng viên có nhiều project, deployment hoặc CI/CD nên fit mạnh hơn exact-fit cơ bản, nhưng vẫn cần giữ điểm trong khoảng kiểm soát."
    if category == "same_role_different_stack":
        return "Cùng role family nhưng khác stack chính; nên có điểm trung bình khá và giải thích rõ stack gap."
    if category == "role_mismatch":
        return "Role family khác nhau nên cần penalty rõ dù vẫn có một ít keyword hoặc kỹ năng kỹ thuật chung."
    if category == "cross_domain_transferable":
        return "Có transferable skills nhưng chưa đủ evidence cho target role chính; điểm nên ở mức trung bình hoặc thấp hơn."
    if category == "weak_cv":
        return "Role có vẻ phù hợp nhưng CV thiếu evidence project/experience nên confidence và score không nên quá cao."
    if category == "keyword_stuffing":
        return "CV chứa keyword liên quan nhưng thiếu evidence meaningful usage; matcher không nên over-score."
    if category == "non_it_mismatch":
        return "Profile không có evidence kỹ thuật phù hợp với JD công nghệ; điểm nên thấp và confidence thấp."
    if category == "career_switch":
        return f"Ứng viên chuyển ngành từ {career_switch_source}; có thể có transferable skills nhưng thiếu evidence kỹ thuật cho target role."
    if category == "missing_critical_skill":
        return f"CV có một phần fit nhưng thiếu critical skills như {', '.join(missing[:3])}; score nên bị giới hạn."
    return "Case synthetic dùng để kiểm tra hành vi matcher trong điều kiện có kiểm soát."


def build_statistics(cases: list[dict[str, Any]]) -> dict[str, Counter[str]]:
    return {
        "role_distribution": Counter(case["target_role"] for case in cases),
        "label_distribution": Counter(case["fit_label"] for case in cases),
        "category_distribution": Counter(case["category"] for case in cases),
        "seniority_distribution": Counter(case["seniority"] for case in cases),
    }


def _markdown_table(counter: Counter[str]) -> str:
    lines = ["| Value | Count |", "| --- | ---: |"]
    for key, value in sorted(counter.items()):
        lines.append(f"| {key} | {value} |")
    return "\n".join(lines)


def write_statistics(cases: list[dict[str, Any]]) -> None:
    stats = build_statistics(cases)
    text = "\n\n".join(
        [
            "# Synthetic Dataset Statistics",
            "Date: 2026-06-22",
            f"Total cases: {len(cases)}",
            "## Role Distribution\n\n" + _markdown_table(stats["role_distribution"]),
            "## Label Distribution\n\n" + _markdown_table(stats["label_distribution"]),
            "## Category Distribution\n\n" + _markdown_table(stats["category_distribution"]),
            "## Seniority Distribution\n\n" + _markdown_table(stats["seniority_distribution"]),
            "## Notes\n\nDataset này là synthetic, không phải real beta data. Các phân phối dùng để kiểm tra coverage, không đại diện cho thị trường tuyển dụng thật.",
        ]
    )
    STATISTICS_FILE.write_text(text + "\n", encoding="utf-8")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    cases = generate_cases()
    payload = {
        "schema_version": "careeros-synthetic-dataset-v2",
        "dataset_type": "synthetic",
        "description": "Synthetic CV/JD matching cases tự tạo, không chứa CV thật, JD thật hoặc PII.",
        "case_count": len(cases),
        "cases": cases,
    }
    OUTPUT_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_statistics(cases)
    print(f"Generated {len(cases)} synthetic cases at {OUTPUT_FILE}")
    print(f"Generated statistics at {STATISTICS_FILE}")


if __name__ == "__main__":
    main()
