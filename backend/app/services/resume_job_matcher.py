from collections import Counter
import os
from pathlib import Path
import re
from typing import Any

from pypdf import PdfReader

SEMANTIC_MODEL_NAME = "all-MiniLM-L6-v2"
SEMANTIC_MODEL: Any | None = None
SEMANTIC_MODEL_LOAD_ERROR: str | None = None

SKILL_ALIASES = {
    "js": "javascript",
    "ts": "typescript",
    "dotnet": ".net",
    "postgres": "postgresql",
    "asp net": "asp.net core",
    "asp.net": "asp.net core",
    "reactjs": "react",
    "nextjs": "next.js",
    "next js": "next.js",
    "nodejs": "node.js",
    "node js": "node.js",
    "ml": "machine learning",
    "k8s": "kubernetes",
    "ci cd": "ci/cd",
    "tailwind css": "tailwind",
}

TECH_SKILLS = sorted(
    {
        "frontend", "backend", "fullstack", "react", "next.js", "angular", "vue",
        "node.js", "express", "fastapi", "django", "flask", "python", "java",
        "c#", "asp.net core", ".net", "sql", "postgresql", "mysql", "mongodb",
        "docker", "git", "github", "rest api", "jwt", "authentication",
        "typescript", "javascript", "html", "css", "tailwind", "flutter",
        "react native", "android", "ios", "kotlin", "swift", "firebase", "supabase",
        "machine learning", "ai", "nlp", "redis", "kubernetes", "graphql", "oauth",
        "testing", "unit testing", "pytest", "ci/cd", "linux", "terraform", "aws",
        "azure", "gcp", "scikit-learn", "pandas", "numpy", "pytorch", "tensorflow",
        "sentence transformers", "api", "database", "orm", "sqlalchemy",
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
    "chÃºng",
    "tÃ´i",
    "báº¡n",
    "cÃ¡c",
    "vá»›i",
    "cho",
    "cá»§a",
    "trong",
    "kinh",
    "nghiá»‡m",
}

PREVIEW_LENGTH = 1200
MIN_TEXT_LENGTH_FOR_SEMANTIC = 80

ROLE_CORE_SKILLS = {
    "backend": {
        "backend", "python", "java", "c#", "fastapi", "django", "flask", "node.js",
        "express", "rest api", "api", "sql", "postgresql", "mysql", "mongodb",
        "database", "authentication", "jwt", "docker",
    },
    "frontend": {
        "frontend", "javascript", "typescript", "react", "next.js", "angular", "vue",
        "html", "css", "tailwind", "authentication", "api",
    },
    "fullstack": {
        "fullstack", "frontend", "backend", "javascript", "typescript", "react", "next.js",
        "angular", "vue", "node.js", "express", "python", "fastapi", "rest api",
        "sql", "postgresql", "authentication", "jwt", "docker",
    },
    "ai": {
        "ai", "machine learning", "nlp", "python", "scikit-learn", "pandas",
        "numpy", "pytorch", "tensorflow", "sentence transformers",
    },
}

ROLE_CORE_SKILLS["ai/data"] = ROLE_CORE_SKILLS["ai"]

ROLE_SIGNALS = {
    "backend": {"backend", "back-end", "back end", "api", "server", "fastapi", "django", "flask", "node.js", "express", "spring", ".net", "asp.net core", "database", "sql", "postgresql", "jwt"},
    "frontend": {"frontend", "front-end", "front end", "react", "next.js", "angular", "vue", "html", "css", "tailwind", "ui", "component"},
    "fullstack": {"fullstack", "full-stack", "full stack", "frontend", "backend", "react", "node.js", "api", "database"},
    "ai/data": {"ai", "machine learning", "ml", "nlp", "data", "pandas", "numpy", "scikit-learn", "pytorch", "tensorflow", "model"},
    "mobile": {"mobile", "flutter", "react native", "android", "ios", "kotlin", "swift", "firebase"},
    "devops": {"devops", "docker", "kubernetes", "k8s", "ci/cd", "linux", "terraform", "aws", "azure", "gcp", "cloud"},
}

ROLE_CORE_SKILLS["mobile"] = {"mobile", "flutter", "react native", "android", "ios", "kotlin", "swift", "firebase"}
ROLE_CORE_SKILLS["devops"] = {"devops", "docker", "kubernetes", "ci/cd", "linux", "terraform", "aws", "azure", "gcp"}
ROLE_CORE_SKILLS["general software"] = {"git", "github", "testing", "unit testing", "api", "rest api", "database", "sql"}

STACK_GROUPS = {
    "python_backend": {"python", "fastapi", "django", "flask"},
    "java_backend": {"java", "spring"},
    "dotnet_backend": {"c#", ".net", "asp.net core"},
    "node_backend": {"node.js", "express"},
    "react_frontend": {"react", "next.js"},
    "angular_frontend": {"angular"},
    "vue_frontend": {"vue"},
    "mobile_flutter": {"flutter"},
    "mobile_native": {"react native", "android", "ios", "kotlin", "swift"},
    "devops_container": {"docker", "kubernetes"},
    "cloud": {"aws", "azure", "gcp", "terraform"},
}

GENERIC_SKILLS = {"git", "github", "api", "rest api", "database", "testing", "unit testing", "html", "css"}
EVIDENCE_TERMS = {"project", "projects", "experience", "internship", "built", "developed", "implemented", "deployed", "designed", "maintained", "integrated", "production", "system", "platform", "du an", "kinh nghiem", "xay dung", "trien khai"}

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

    resume_role = _detect_role_family(resume_text, resume_skills)
    jd_role = _detect_role_family(job_description_text, jd_skills)
    role_context = _detect_role_context(job_description_text)
    resume_stacks = _detect_stack_groups(resume_skills, resume_text)
    jd_stacks = _detect_stack_groups(jd_skills, job_description_text)
    critical_skills = _critical_jd_skills(jd_skills, jd_role["primary"], job_description_text)

    prioritized_missing_skills = _prioritize_missing_skills(missing_skills, role_context, job_description_text)
    skill_gap_summary = _build_skill_gap_summary(prioritized_missing_skills, role_context)
    improvement_plan = _build_improvement_plan(prioritized_missing_skills, resume_text, job_description_text)
    overlapping_keywords = _keyword_overlap(resume_text, job_description_text)
    semantic_score, semantic_available = _semantic_score(resume_text, job_description_text)

    base_role_score, role_notes = _role_alignment_score(resume_role, jd_role, resume_stacks, jd_stacks)
    base_evidence_score, evidence_notes = _evidence_score(resume_text, matched_skills)
    confidence = _confidence_signal(resume_text, job_description_text, base_evidence_score, resume_skills, jd_skills)

    if semantic_available:
        skill_score = round(_weighted_skill_score(matched_skills, jd_skills, critical_skills, jd_role["primary"], max_score=35.0), 1)
        keyword_score = round(_keyword_score(overlapping_keywords, job_description_text, max_score=15.0), 1)
        role_alignment_score = round(min(base_role_score, 15.0), 1)
        evidence_score = round(min(base_evidence_score, 15.0), 1)
        length_sanity = round(_length_sanity_score(resume_text, job_description_text, max_score=5.0), 1)
        raw_score = skill_score + keyword_score + semantic_score + role_alignment_score + evidence_score + length_sanity
    else:
        skill_score = round(_weighted_skill_score(matched_skills, jd_skills, critical_skills, jd_role["primary"], max_score=40.0), 1)
        keyword_score = round(_keyword_score(overlapping_keywords, job_description_text, max_score=15.0), 1)
        role_alignment_score = round(min(base_role_score * (20.0 / 15.0), 20.0), 1)
        evidence_score = round(min(base_evidence_score * (20.0 / 15.0), 20.0), 1)
        length_sanity = round(_length_sanity_score(resume_text, job_description_text, max_score=5.0), 1)
        raw_score = skill_score + keyword_score + role_alignment_score + evidence_score + length_sanity

    final_score = round(_apply_confidence_cap(min(100.0, raw_score), confidence), 1)
    suggestions = _build_suggestions(
        missing_skills=missing_skills,
        resume_text=resume_text,
        job_description_text=job_description_text,
        semantic_score=semantic_score,
        semantic_available=semantic_available,
    )
    suggestions.extend(_v2_suggestions(resume_role, jd_role, resume_stacks, jd_stacks, critical_skills, confidence, evidence_score))

    return {
        "match_score": final_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "keyword_overlap": overlapping_keywords,
        "skill_gap_summary": skill_gap_summary,
        "prioritized_missing_skills": prioritized_missing_skills,
        "improvement_plan": improvement_plan,
        "summary": _build_summary(final_score, matched_skills, missing_skills, semantic_score, semantic_available),
        "suggestions": _dedupe_preserve_order(suggestions)[:10],
        "resume_text_preview": build_text_preview(resume_text),
        "jd_text_preview": build_text_preview(job_description_text),
        "resume_detected_skills": resume_skills,
        "jd_detected_skills": jd_skills,
        "scoring_breakdown": {
            "skill_score": skill_score,
            "keyword_score": keyword_score,
            "semantic_score": semantic_score,
            "role_alignment_score": role_alignment_score,
            "evidence_score": evidence_score,
            "length_sanity": length_sanity,
            "confidence": confidence,
            "final_score": final_score,
            "resume_role_family": resume_role["primary"],
            "jd_role_family": jd_role["primary"],
            "resume_role_signals": resume_role["signals"],
            "jd_role_signals": jd_role["signals"],
            "resume_stack_groups": resume_stacks,
            "jd_stack_groups": jd_stacks,
            "critical_skills": critical_skills,
            "role_alignment_notes": role_notes,
            "evidence_notes": evidence_notes,
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
    normalized = normalized.replace("react js", "react").replace("reactjs", "react")
    normalized = normalized.replace("dotnet", ".net").replace("postgres", "postgresql")
    normalized = normalized.replace("asp net", "asp.net")
    normalized = normalized.replace("ci cd", "ci/cd").replace("k8s", "kubernetes")
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


def _skill_score(matched_skills: list[str], jd_skills: list[str], max_score: float) -> float:
    if not jd_skills:
        return min(20.0, max_score) if matched_skills else 0.0
    return (len(matched_skills) / len(set(jd_skills))) * max_score


def _keyword_score(overlapping_keywords: list[str], job_description_text: str, max_score: float) -> float:
    jd_keyword_count = max(len(_keywords(job_description_text)), 1)
    return min(max_score, (len(overlapping_keywords) / min(jd_keyword_count, 30)) * max_score)


def _length_sanity_score(resume_text: str, job_description_text: str, max_score: float) -> float:
    resume_length = len(resume_text.strip())
    jd_length = len(job_description_text.strip())
    if resume_length >= 800 and jd_length >= 300:
        return max_score
    if resume_length >= 400 and jd_length >= 150:
        return max_score * 0.6
    if resume_length >= 150 and jd_length >= 80:
        return max_score * 0.3
    return 0.0

def _weighted_skill_score(
    matched_skills: list[str], jd_skills: list[str], critical_skills: list[str], role_family: str, max_score: float
) -> float:
    if not jd_skills:
        return min(15.0, max_score) if matched_skills else 0.0
    matched = set(matched_skills)
    critical = set(critical_skills)
    role_core = ROLE_CORE_SKILLS.get(role_family, set())
    total_weight = 0.0
    matched_weight = 0.0
    for skill in set(jd_skills):
        weight = 1.0
        if skill in critical:
            weight = 2.5
        elif skill in role_core:
            weight = 1.6
        elif skill in GENERIC_SKILLS:
            weight = 0.6
        total_weight += weight
        if skill in matched:
            matched_weight += weight
    return 0.0 if total_weight == 0 else (matched_weight / total_weight) * max_score


def _detect_role_family(text: str, skills: list[str]) -> dict[str, Any]:
    normalized = _normalize(text)
    scores: dict[str, int] = {}
    signals: dict[str, list[str]] = {}
    for role, role_signals in ROLE_SIGNALS.items():
        hits = sorted(signal for signal in role_signals if _contains_skill(normalized, signal))
        skill_hits = sorted(set(skills).intersection(ROLE_CORE_SKILLS.get(role, set())))
        combined = sorted(set(hits + skill_hits))
        if combined:
            scores[role] = len(hits) + len(skill_hits)
            signals[role] = combined[:8]
    if scores.get("backend", 0) > 0 and scores.get("frontend", 0) > 0:
        scores["fullstack"] = max(scores.get("fullstack", 0), min(scores["backend"], scores["frontend"]) + 2)
        signals["fullstack"] = sorted(set(signals.get("fullstack", []) + signals.get("backend", [])[:3] + signals.get("frontend", [])[:3]))[:8]
    if not scores:
        return {"primary": "general software", "detected": ["general software"], "signals": {"general software": []}}
    primary = sorted(scores.items(), key=lambda item: item[1], reverse=True)[0][0]
    detected = [role for role, score in sorted(scores.items(), key=lambda item: item[1], reverse=True) if score > 0]
    return {"primary": primary, "detected": detected, "signals": signals}


def _detect_stack_groups(skills: list[str], text: str) -> list[str]:
    normalized = _normalize(text)
    skill_set = set(skills)
    detected = []
    for stack_name, stack_skills in STACK_GROUPS.items():
        if skill_set.intersection(stack_skills) or any(_contains_skill(normalized, skill) for skill in stack_skills):
            detected.append(stack_name)
    return sorted(set(detected))


def _critical_jd_skills(jd_skills: list[str], role_family: str, job_description_text: str) -> list[str]:
    role_core = ROLE_CORE_SKILLS.get(role_family, set())
    jd_keywords = _keywords(job_description_text)
    critical = []
    for skill in jd_skills:
        frequency = jd_keywords.get(_normalize(skill), 0)
        if skill in role_core and skill not in GENERIC_SKILLS:
            critical.append(skill)
        elif frequency >= 2 and skill not in GENERIC_SKILLS:
            critical.append(skill)
    return sorted(set(critical))


def _role_alignment_score(
    resume_role: dict[str, Any], jd_role: dict[str, Any], resume_stacks: list[str], jd_stacks: list[str]
) -> tuple[float, list[str]]:
    resume_primary = resume_role["primary"]
    jd_primary = jd_role["primary"]
    notes = [f"CV role family: {resume_primary}", f"JD role family: {jd_primary}"]
    if jd_primary == "general software" or resume_primary == "general software":
        score = 10.0
    elif resume_primary == jd_primary:
        score = 15.0
    elif "fullstack" in {resume_primary, jd_primary} and {resume_primary, jd_primary}.intersection({"backend", "frontend"}):
        score = 11.0
        notes.append("Fullstack/backend/frontend are partially aligned, but not exact.")
    elif {resume_primary, jd_primary} == {"backend", "frontend"}:
        score = 4.0
        notes.append("Strong role mismatch between backend and frontend signals.")
    elif {resume_primary, jd_primary}.intersection({"ai/data", "devops", "mobile"}):
        score = 6.0
        notes.append("Specialized role family differs from the JD target.")
    else:
        score = 8.0
        notes.append("Role families are adjacent but not exact.")
    if jd_stacks:
        stack_overlap = set(resume_stacks).intersection(jd_stacks)
        if stack_overlap:
            notes.append(f"Stack overlap: {', '.join(sorted(stack_overlap))}.")
        elif _has_backend_stack(resume_stacks) and _has_backend_stack(jd_stacks) or _has_frontend_stack(resume_stacks) and _has_frontend_stack(jd_stacks):
            score -= 3.0
            notes.append("Same role family but different primary stack.")
        else:
            score -= 5.0
            notes.append("No clear stack overlap with the JD.")
    return max(0.0, score), notes


def _has_backend_stack(stacks: list[str]) -> bool:
    return any(stack in stacks for stack in ("python_backend", "java_backend", "dotnet_backend", "node_backend"))


def _has_frontend_stack(stacks: list[str]) -> bool:
    return any(stack in stacks for stack in ("react_frontend", "angular_frontend", "vue_frontend"))


def _evidence_score(resume_text: str, matched_skills: list[str]) -> tuple[float, list[str]]:
    if not matched_skills:
        return 0.0, ["No matched skills to evaluate for evidence."]
    scores = []
    strong = []
    weak = []
    for skill in matched_skills:
        level, count = _skill_evidence_level(resume_text, skill)
        if level == "strong":
            value = 1.0
            strong.append(skill)
        elif level == "medium":
            value = 0.65
        else:
            value = 0.3
            weak.append(skill)
        if count >= 3:
            value = min(1.0, value + 0.15)
        scores.append(value)
    notes = []
    if strong:
        notes.append(f"Strong project/experience evidence: {', '.join(strong[:5])}.")
    if weak:
        notes.append(f"Mostly keyword-level evidence: {', '.join(weak[:5])}.")
    if not notes:
        notes.append("Matched skills have moderate evidence in the CV text.")
    return (sum(scores) / len(scores)) * 15.0, notes


def _skill_evidence_level(text: str, skill: str) -> tuple[str, int]:
    normalized = _normalize(text)
    occurrences = list(re.finditer(re.escape(_normalize(skill)), normalized))
    if not occurrences:
        return "weak", 0
    evidence_hits = 0
    for occurrence in occurrences:
        start = max(0, occurrence.start() - 140)
        end = min(len(normalized), occurrence.end() + 140)
        window = normalized[start:end]
        if any(term in window for term in EVIDENCE_TERMS):
            evidence_hits += 1
    if evidence_hits >= 1 and len(occurrences) >= 2:
        return "strong", len(occurrences)
    if evidence_hits >= 1 or len(occurrences) >= 2:
        return "medium", len(occurrences)
    return "weak", len(occurrences)


def _confidence_signal(
    resume_text: str, job_description_text: str, evidence_score: float, resume_skills: list[str], jd_skills: list[str]
) -> str:
    resume_length = len(resume_text.strip())
    jd_length = len(job_description_text.strip())
    if resume_length < 120 or jd_length < 80 or not resume_skills or not jd_skills:
        return "low"
    if resume_length < 300 and evidence_score < 6:
        return "low"
    if resume_length >= 900 and jd_length >= 300 and evidence_score >= 10 and len(resume_skills) >= 5 and len(jd_skills) >= 4:
        return "high"
    return "medium"


def _apply_confidence_cap(score: float, confidence: str) -> float:
    if confidence == "low":
        return min(score, 65.0)
    if confidence == "medium":
        return min(score, 90.0)
    return score


def _v2_suggestions(
    resume_role: dict[str, Any], jd_role: dict[str, Any], resume_stacks: list[str], jd_stacks: list[str], critical_skills: list[str], confidence: str, evidence_score: float
) -> list[str]:
    suggestions = []
    resume_primary = resume_role["primary"]
    jd_primary = jd_role["primary"]
    if resume_primary != jd_primary and jd_primary != "general software":
        suggestions.append(f"Role alignment needs attention: CV currently looks closer to {resume_primary}, while this JD looks closer to {jd_primary}.")
    if jd_stacks and not set(resume_stacks).intersection(jd_stacks):
        suggestions.append(f"Stack mismatch: JD stack signals include {', '.join(jd_stacks[:4])}, but CV stack signals include {', '.join(resume_stacks[:4]) or 'none detected'}.")
    if critical_skills:
        suggestions.append(f"Critical JD skills to prove first: {', '.join(critical_skills[:6])}.")
    if confidence == "low":
        suggestions.append("Confidence is low because the available CV/JD text or detected evidence is limited; verify the extracted preview before trusting the score.")
    if evidence_score < 6:
        suggestions.append("Matched skills appear mostly as keywords. Move the most important ones into project/experience bullets with concrete outcomes.")
    return suggestions


def _semantic_score(resume_text: str, job_description_text: str) -> tuple[float, bool]:
    if len(resume_text.strip()) < MIN_TEXT_LENGTH_FOR_SEMANTIC or len(job_description_text.strip()) < MIN_TEXT_LENGTH_FOR_SEMANTIC:
        return 0.0, False

    model = _get_semantic_model()
    if model is None:
        return 0.0, False

    try:
        embeddings = model.encode(
            [resume_text, job_description_text],
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        cosine_similarity = float(embeddings[0] @ embeddings[1])
        normalized_similarity = max(0.0, min(1.0, cosine_similarity))
        return round(normalized_similarity * 15.0, 1), True
    except Exception:
        return 0.0, False


def _get_semantic_model() -> Any | None:
    global SEMANTIC_MODEL, SEMANTIC_MODEL_LOAD_ERROR

    if not _sentence_transformers_enabled():
        return None
    if SEMANTIC_MODEL is not None:
        return SEMANTIC_MODEL
    if SEMANTIC_MODEL_LOAD_ERROR is not None:
        return None

    try:
        from sentence_transformers import SentenceTransformer

        local_files_only = os.getenv("SENTENCE_TRANSFORMERS_LOCAL_FILES_ONLY", "true").lower() != "false"
        SEMANTIC_MODEL = SentenceTransformer(SEMANTIC_MODEL_NAME, local_files_only=local_files_only)
        return SEMANTIC_MODEL
    except Exception as exc:
        SEMANTIC_MODEL_LOAD_ERROR = str(exc)
        return None


def _sentence_transformers_enabled() -> bool:
    return os.getenv("SENTENCE_TRANSFORMERS_ENABLED", "false").strip().lower() == "true"


def _build_summary(
    match_score: float,
    matched_skills: list[str],
    missing_skills: list[str],
    semantic_score: float,
    semantic_available: bool,
) -> str:
    if match_score >= 80:
        level = "má»©c Ä‘á»™ phÃ¹ há»£p cao"
    elif match_score >= 60:
        level = "má»©c Ä‘á»™ phÃ¹ há»£p khÃ¡"
    elif match_score >= 40:
        level = "má»©c Ä‘á»™ phÃ¹ há»£p trung bÃ¬nh"
    else:
        level = "má»©c Ä‘á»™ phÃ¹ há»£p cÃ²n tháº¥p"

    matched_text = ", ".join(matched_skills[:5]) if matched_skills else "chÆ°a phÃ¡t hiá»‡n ká»¹ nÄƒng trÃ¹ng khá»›p rÃµ rÃ ng"
    missing_text = ", ".join(missing_skills[:5]) if missing_skills else "khÃ´ng cÃ³ skill gap lá»›n trong danh sÃ¡ch ká»¹ nÄƒng hiá»‡n táº¡i"
    semantic_text = (
        f"Semantic score hiá»‡n lÃ  {semantic_score}/15."
        if semantic_available
        else "Semantic score chÆ°a kháº£ dá»¥ng, há»‡ thá»‘ng Ä‘ang fallback vá» rule-based scoring."
    )
    return f"CV cÃ³ {level} vá»›i JD. Äiá»ƒm máº¡nh chÃ­nh: {matched_text}. Khoáº£ng trá»‘ng cáº§n chÃº Ã½: {missing_text}. {semantic_text}"


def _build_suggestions(
    missing_skills: list[str],
    resume_text: str,
    job_description_text: str,
    semantic_score: float,
    semantic_available: bool,
) -> list[str]:
    suggestions = []
    if len(missing_skills) >= 4:
        top_missing = ", ".join(missing_skills[:8])
        suggestions.append(f"JD Ä‘ang yÃªu cáº§u nhiá»u ká»¹ nÄƒng CV chÆ°a thá»ƒ hiá»‡n rÃµ. Æ¯u tiÃªn bá»• sung hoáº·c chá»©ng minh kinh nghiá»‡m vá»›i: {top_missing}.")
    elif missing_skills:
        top_missing = ", ".join(missing_skills[:5])
        suggestions.append(f"Bá»• sung hoáº·c lÃ m rÃµ kinh nghiá»‡m liÃªn quan Ä‘áº¿n: {top_missing}.")

    if semantic_available and semantic_score < 10:
        suggestions.append("Semantic score tháº¥p: nÃªn viáº¿t láº¡i pháº§n project/experience sÃ¡t JD hÆ¡n, dÃ¹ng mÃ´ táº£ trÃ¡ch nhiá»‡m, domain vÃ  impact gáº§n vá»›i vá»‹ trÃ­ má»¥c tiÃªu.")
    elif semantic_available and semantic_score < 16:
        suggestions.append("Semantic score á»Ÿ má»©c trung bÃ¬nh: hÃ£y lÃ m rÃµ project nÃ o liÃªn quan trá»±c tiáº¿p Ä‘áº¿n trÃ¡ch nhiá»‡m trong JD thay vÃ¬ chá»‰ liá»‡t kÃª tech stack.")
    elif not semantic_available:
        suggestions.append("Semantic score chÆ°a kháº£ dá»¥ng trong láº§n phÃ¢n tÃ­ch nÃ y; hÃ£y dá»±a vÃ o skill gap, keyword overlap vÃ  text preview Ä‘á»ƒ kiá»ƒm chá»©ng káº¿t quáº£.")

    suggestions.append("Äiá»u chá»‰nh CV theo JD báº±ng cÃ¡ch Ä‘Æ°a cÃ¡c keyword quan trá»ng vÃ o pháº§n project, experience vÃ  skills náº¿u pháº£n Ã¡nh Ä‘Ãºng nÄƒng lá»±c tháº­t.")
    if len(resume_text.strip()) < 800:
        suggestions.append("CV Ä‘ang khÃ¡ ngáº¯n sau khi trÃ­ch xuáº¥t text; nÃªn mÃ´ táº£ project báº±ng impact, tech stack, vai trÃ² cÃ¡ nhÃ¢n vÃ  káº¿t quáº£ cá»¥ thá»ƒ.")
    if len(job_description_text.strip()) < 300:
        suggestions.append("JD Ä‘ang khÃ¡ ngáº¯n; káº¿t quáº£ matching sáº½ tá»‘t hÆ¡n náº¿u JD cÃ³ Ä‘á»§ trÃ¡ch nhiá»‡m, yÃªu cáº§u ká»¹ nÄƒng vÃ  tiÃªu chÃ­ Æ°u tiÃªn.")
    suggestions.append("Æ¯u tiÃªn cáº£i thiá»‡n cÃ¡c skill gap xuáº¥t hiá»‡n trá»±c tiáº¿p trong JD trÆ°á»›c khi má»Ÿ rá»™ng sang ká»¹ nÄƒng ngoÃ i pháº¡m vi vá»‹ trÃ­ nÃ y.")
    return suggestions

def _detect_role_context(job_description_text: str) -> list[str]:
    role_info = _detect_role_family(job_description_text, extract_skills(job_description_text))
    return role_info["detected"] or ["general software"]
def _prioritize_missing_skills(
    missing_skills: list[str], role_context: list[str], job_description_text: str
) -> dict[str, list[str]]:
    priority_groups: dict[str, list[str]] = {
        "high_priority": [],
        "medium_priority": [],
        "low_priority": [],
    }
    if not missing_skills:
        return priority_groups

    jd_keywords = _keywords(job_description_text)
    core_skills = set()
    for role in role_context:
        core_skills.update(ROLE_CORE_SKILLS.get(role, set()))

    for skill in missing_skills:
        skill_frequency = jd_keywords.get(skill, 0)
        is_core_for_role = skill in core_skills
        is_found_in_jd = _contains_skill(_normalize(job_description_text), skill)

        if is_core_for_role and (skill_frequency > 1 or is_found_in_jd):
            priority_groups["high_priority"].append(skill)
        elif is_core_for_role or skill_frequency > 1 or skill in {"authentication", "jwt", "rest api", "database", "sql"}:
            priority_groups["medium_priority"].append(skill)
        else:
            priority_groups["low_priority"].append(skill)

    return {key: sorted(set(value)) for key, value in priority_groups.items()}


def _build_skill_gap_summary(prioritized_missing_skills: dict[str, list[str]], role_context: list[str]) -> str:
    high_count = len(prioritized_missing_skills["high_priority"])
    medium_count = len(prioritized_missing_skills["medium_priority"])
    low_count = len(prioritized_missing_skills["low_priority"])
    total_missing = high_count + medium_count + low_count
    role_text = ", ".join(role_context) if role_context != ["general"] else "vai trÃ² má»¥c tiÃªu"

    if total_missing == 0:
        return "ChÆ°a phÃ¡t hiá»‡n skill gap rÃµ rÃ ng so vá»›i JD. CV Ä‘ang bao phá»§ tá»‘t cÃ¡c ká»¹ nÄƒng há»‡ thá»‘ng nháº­n diá»‡n Ä‘Æ°á»£c, nÃªn Æ°u tiÃªn cáº£i thiá»‡n cÃ¡ch trÃ¬nh bÃ y cho sÃ¡t JD hÆ¡n."
    if high_count > 0:
        return f"PhÃ¡t hiá»‡n {total_missing} ká»¹ nÄƒng cÃ²n thiáº¿u cho {role_text}, trong Ä‘Ã³ {high_count} ká»¹ nÄƒng thuá»™c nhÃ³m Æ°u tiÃªn cao cáº§n xá»­ lÃ½ trÆ°á»›c."
    if medium_count > 0:
        return f"PhÃ¡t hiá»‡n {total_missing} ká»¹ nÄƒng cÃ²n thiáº¿u cho {role_text}. ChÆ°a cÃ³ gap Æ°u tiÃªn cao, nhÆ°ng cÃ³ {medium_count} ká»¹ nÄƒng nÃªn lÃ m rÃµ hoáº·c bá»• sung."
    return f"PhÃ¡t hiá»‡n {total_missing} ká»¹ nÄƒng cÃ²n thiáº¿u, chá»§ yáº¿u á»Ÿ má»©c Æ°u tiÃªn tháº¥p. CV cÃ³ thá»ƒ cáº£i thiá»‡n báº±ng cÃ¡ch alignment tá»‘t hÆ¡n vá»›i JD."


def _build_improvement_plan(
    prioritized_missing_skills: dict[str, list[str]], resume_text: str, job_description_text: str
) -> list[str]:
    plan = []
    high_priority = prioritized_missing_skills["high_priority"]
    medium_priority = prioritized_missing_skills["medium_priority"]
    low_priority = prioritized_missing_skills["low_priority"]

    for skill in high_priority[:5]:
        plan.append(_skill_action(skill, urgent=True))
    for skill in medium_priority[:4]:
        plan.append(_skill_action(skill, urgent=False))

    if not high_priority and not medium_priority and low_priority:
        plan.append(f"CÃ¡c ká»¹ nÄƒng cÃ²n thiáº¿u Ä‘ang á»Ÿ má»©c Æ°u tiÃªn tháº¥p ({', '.join(low_priority[:5])}). Chá»‰ bá»• sung vÃ o CV náº¿u báº¡n thá»±c sá»± Ä‘Ã£ dÃ¹ng trong project hoáº·c kinh nghiá»‡m thá»±c táº¿.")

    if not high_priority and not medium_priority and not low_priority:
        plan.append("Giá»¯ nguyÃªn skill set chÃ­nh, nhÆ°ng viáº¿t láº¡i pháº§n project/experience Ä‘á»ƒ bÃ¡m sÃ¡t ngÃ´n ngá»¯ trong JD hÆ¡n.")

    if any(skill in high_priority + medium_priority for skill in ("rest api", "api", "database", "postgresql", "sql", "authentication", "jwt")):
        plan.append("Viáº¿t láº¡i pháº§n project Ä‘á»ƒ thá»ƒ hiá»‡n rÃµ REST API, database, authentication, vai trÃ² cÃ¡ nhÃ¢n vÃ  káº¿t quáº£ Ä‘áº¡t Ä‘Æ°á»£c.")
    if len(resume_text.strip()) < 800:
        plan.append("CV text Ä‘ang ngáº¯n; bá»• sung mÃ´ táº£ project theo cáº¥u trÃºc: váº¥n Ä‘á», tech stack, pháº§n báº¡n lÃ m, káº¿t quáº£ hoáº·c impact.")
    if len(job_description_text.strip()) < 300:
        plan.append("JD Ä‘ang ngáº¯n; náº¿u cÃ³ thá»ƒ, dÃ¹ng JD Ä‘áº§y Ä‘á»§ hÆ¡n Ä‘á»ƒ há»‡ thá»‘ng phÃ¢n tÃ­ch skill gap chÃ­nh xÃ¡c hÆ¡n.")

    return _dedupe_preserve_order(plan)[:8]


def _skill_action(skill: str, urgent: bool) -> str:
    prefix = "Æ¯u tiÃªn cao" if urgent else "Æ¯u tiÃªn trung bÃ¬nh"
    if skill == "docker":
        return f"{prefix}: Náº¿u Ä‘Ã£ dÃ¹ng Docker, bá»• sung project hoáº·c kinh nghiá»‡m liÃªn quan. Náº¿u chÆ°a biáº¿t Docker, há»c Docker cÆ¡ báº£n trÆ°á»›c khi apply vá»‹ trÃ­ nÃ y."
    if skill in {"rest api", "api"}:
        return f"{prefix}: LÃ m rÃµ kinh nghiá»‡m thiáº¿t káº¿ REST API, endpoint CRUD, validation, error handling vÃ  authentication trong project."
    if skill in {"database", "sql", "postgresql", "mysql", "mongodb"}:
        return f"{prefix}: Bá»• sung pháº§n database: schema, query, relationship, migration hoáº·c tá»‘i Æ°u truy váº¥n náº¿u báº¡n Ä‘Ã£ lÃ m."
    if skill in {"authentication", "jwt", "oauth"}:
        return f"{prefix}: Thá»ƒ hiá»‡n rÃµ kinh nghiá»‡m authentication, JWT/token flow, báº£o vá»‡ endpoint vÃ  xá»­ lÃ½ quyá»n truy cáº­p."
    if skill in {"react", "next.js", "typescript", "javascript", "html", "css", "tailwind"}:
        return f"{prefix}: Bá»• sung vÃ­ dá»¥ frontend liÃªn quan Ä‘áº¿n {skill}, nháº¥t lÃ  component, state, form, API integration vÃ  UI production-ready."
    if skill in {"machine learning", "ai", "nlp", "scikit-learn", "pytorch", "tensorflow", "sentence transformers"}:
        return f"{prefix}: Bá»• sung project AI/ML liÃªn quan Ä‘áº¿n {skill}, nÃªu rÃµ dá»¯ liá»‡u Ä‘áº§u vÃ o, cÃ¡ch Ä‘Ã¡nh giÃ¡ vÃ  káº¿t quáº£."
    return f"{prefix}: Bá»• sung hoáº·c há»c ná»n táº£ng {skill}; chá»‰ Ä‘Æ°a vÃ o CV khi báº¡n cÃ³ project, bÃ i lab hoáº·c kinh nghiá»‡m Ä‘á»§ chá»©ng minh."


def _dedupe_preserve_order(items: list[str]) -> list[str]:
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            result.append(item)
            seen.add(item)
    return result











