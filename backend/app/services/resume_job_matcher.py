from collections import Counter
from pathlib import Path
import re

from pypdf import PdfReader

SKILL_ALIASES = {
    "js": "javascript",
    "ts": "typescript",
    "dotnet": ".net",
    "postgres": "postgresql",
    "asp net": "asp.net core",
    "asp.net": "asp.net core",
    "nextjs": "next.js",
    "next js": "next.js",
    "nodejs": "node.js",
    "node js": "node.js",
    "tailwind css": "tailwind",
}

TECH_SKILLS = sorted(
    {
        "frontend",
        "backend",
        "fullstack",
        "react",
        "next.js",
        "node.js",
        "express",
        "fastapi",
        "django",
        "flask",
        "python",
        "java",
        "c#",
        "asp.net core",
        ".net",
        "sql",
        "postgresql",
        "mysql",
        "mongodb",
        "docker",
        "git",
        "github",
        "rest api",
        "jwt",
        "authentication",
        "typescript",
        "javascript",
        "html",
        "css",
        "tailwind",
        "flutter",
        "firebase",
        "supabase",
        "machine learning",
        "ai",
        "nlp",
        "redis",
        "kubernetes",
        "graphql",
        "oauth",
        "testing",
        "unit testing",
        "pytest",
        "ci/cd",
        "linux",
        "aws",
        "azure",
        "gcp",
        "scikit-learn",
        "pandas",
        "numpy",
        "pytorch",
        "tensorflow",
        "sentence transformers",
        "api",
        "database",
        "orm",
        "sqlalchemy",
    }
)

STOPWORDS = {
    "and",
    "are",
    "for",
    "from",
    "the",
    "this",
    "that",
    "with",
    "you",
    "your",
    "will",
    "have",
    "has",
    "can",
    "our",
    "their",
    "job",
    "role",
    "team",
    "work",
    "experience",
    "skills",
    "candidate",
    "developer",
    "engineer",
    "chúng",
    "tôi",
    "bạn",
    "các",
    "với",
    "cho",
    "của",
    "trong",
    "kinh",
    "nghiệm",
}

PREVIEW_LENGTH = 1200


def extract_pdf_text(storage_path: str) -> str:
    file_path = Path(storage_path)
    if not file_path.exists():
        raise FileNotFoundError(f"PDF file not found: {storage_path}")

    reader = PdfReader(str(file_path))
    page_texts = [(page.extract_text() or "") for page in reader.pages]
    return "\n".join(page_texts).strip()


def extract_txt_text(content: bytes) -> str:
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return content.decode(encoding).strip()
        except UnicodeDecodeError:
            continue
    return content.decode("utf-8", errors="ignore").strip()


def analyze_resume_job_match(resume_text: str, job_description_text: str) -> dict[str, object]:
    resume_text = resume_text or ""
    job_description_text = job_description_text or ""

    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(job_description_text)
    matched_skills = sorted(set(resume_skills).intersection(jd_skills))
    missing_skills = sorted(set(jd_skills).difference(resume_skills))
    overlapping_keywords = _keyword_overlap(resume_text, job_description_text)

    skill_score = round(_skill_score(matched_skills, jd_skills), 1)
    keyword_score = round(_keyword_score(overlapping_keywords, job_description_text), 1)
    length_score = round(_length_sanity_score(resume_text, job_description_text), 1)
    match_score = round(min(100, skill_score + keyword_score + length_score), 1)

    return {
        "match_score": match_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "keyword_overlap": overlapping_keywords,
        "summary": _build_summary(match_score, matched_skills, missing_skills),
        "suggestions": _build_suggestions(missing_skills, resume_text, job_description_text),
        "resume_text_preview": build_text_preview(resume_text),
        "jd_text_preview": build_text_preview(job_description_text),
        "resume_detected_skills": resume_skills,
        "jd_detected_skills": jd_skills,
        "scoring_breakdown": {
            "skill_score": skill_score,
            "keyword_score": keyword_score,
            "length_score": length_score,
            "final_score": match_score,
        },
    }


def build_text_preview(text: str, limit: int = PREVIEW_LENGTH) -> str:
    cleaned = re.sub(r"\s+", " ", (text or "")).strip()
    if len(cleaned) <= limit:
        return cleaned
    return f"{cleaned[:limit].rstrip()}..."


def extract_skills(text: str) -> list[str]:
    normalized = _normalize(text)
    found = []
    for alias, canonical in SKILL_ALIASES.items():
        if _contains_skill(normalized, alias):
            found.append(canonical)
    for skill in TECH_SKILLS:
        if _contains_skill(normalized, skill):
            found.append(skill)
    return sorted(set(found))


def _normalize(text: str) -> str:
    normalized = text.lower()
    normalized = normalized.replace("node js", "node.js").replace("next js", "next.js")
    normalized = normalized.replace("asp net", "asp.net")
    normalized = normalized.replace("ci cd", "ci/cd")
    return normalized


def _contains_skill(normalized_text: str, skill: str) -> bool:
    normalized_skill = _normalize(skill)
    pattern = rf"(?<![a-z0-9+#.]){re.escape(normalized_skill)}(?![a-z0-9+#.])"
    return re.search(pattern, normalized_text) is not None


def _keywords(text: str) -> Counter[str]:
    tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9+#./-]{2,}", _normalize(text))
    return Counter(token for token in tokens if token not in STOPWORDS)


def _keyword_overlap(resume_text: str, job_description_text: str) -> list[str]:
    resume_keywords = _keywords(resume_text)
    jd_keywords = _keywords(job_description_text)
    overlap = set(resume_keywords).intersection(jd_keywords)
    ranked = sorted(overlap, key=lambda word: jd_keywords[word] + resume_keywords[word], reverse=True)
    return ranked[:25]


def _skill_score(matched_skills: list[str], jd_skills: list[str]) -> float:
    if not jd_skills:
        return 20.0 if matched_skills else 0.0
    return (len(matched_skills) / len(set(jd_skills))) * 65.0


def _keyword_score(overlapping_keywords: list[str], job_description_text: str) -> float:
    jd_keyword_count = max(len(_keywords(job_description_text)), 1)
    return min(25.0, (len(overlapping_keywords) / min(jd_keyword_count, 30)) * 25.0)


def _length_sanity_score(resume_text: str, job_description_text: str) -> float:
    resume_length = len(resume_text.strip())
    jd_length = len(job_description_text.strip())
    if resume_length >= 800 and jd_length >= 300:
        return 10.0
    if resume_length >= 400 and jd_length >= 150:
        return 6.0
    if resume_length >= 150 and jd_length >= 80:
        return 3.0
    return 0.0


def _build_summary(match_score: float, matched_skills: list[str], missing_skills: list[str]) -> str:
    if match_score >= 80:
        level = "mức độ phù hợp cao"
    elif match_score >= 60:
        level = "mức độ phù hợp khá"
    elif match_score >= 40:
        level = "mức độ phù hợp trung bình"
    else:
        level = "mức độ phù hợp còn thấp"

    matched_text = ", ".join(matched_skills[:5]) if matched_skills else "chưa phát hiện kỹ năng trùng khớp rõ ràng"
    missing_text = ", ".join(missing_skills[:5]) if missing_skills else "không có skill gap lớn trong danh sách kỹ năng hiện tại"
    return f"CV có {level} với JD. Điểm mạnh chính: {matched_text}. Khoảng trống cần chú ý: {missing_text}."


def _build_suggestions(missing_skills: list[str], resume_text: str, job_description_text: str) -> list[str]:
    suggestions = []
    if missing_skills:
        top_missing = ", ".join(missing_skills[:5])
        suggestions.append(f"Bổ sung hoặc làm rõ kinh nghiệm liên quan đến: {top_missing}.")
    suggestions.append("Điều chỉnh CV theo JD bằng cách đưa các keyword quan trọng vào phần project, experience và skills nếu phản ánh đúng năng lực thật.")
    if len(resume_text.strip()) < 800:
        suggestions.append("CV đang khá ngắn sau khi trích xuất text; nên mô tả project bằng impact, tech stack, vai trò cá nhân và kết quả cụ thể.")
    if len(job_description_text.strip()) < 300:
        suggestions.append("JD đang khá ngắn; kết quả matching sẽ tốt hơn nếu JD có đủ trách nhiệm, yêu cầu kỹ năng và tiêu chí ưu tiên.")
    suggestions.append("Ưu tiên cải thiện các skill gap xuất hiện trực tiếp trong JD trước khi mở rộng sang kỹ năng ngoài phạm vi vị trí này.")
    return suggestions