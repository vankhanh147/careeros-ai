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
    "and", "are", "for", "from", "the", "this", "that", "with", "you", "your",
    "will", "have", "has", "can", "our", "their", "job", "role", "team", "work",
    "experience", "skills", "candidate", "developer", "engineer",
    "ch\u00fang", "t\u00f4i", "b\u1ea1n", "c\u00e1c", "v\u1edbi", "cho", "c\u1ee7a", "trong", "kinh", "nghi\u1ec7m",
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
NEGATION_TERMS = {
    "no", "not", "without", "lack", "lacks", "missing",
    "khong", "kh?ng", "chua", "ch?a", "khong co", "kh?ng c?",
}

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
    resume_feedback = _build_resume_feedback(
        resume_text=resume_text,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        critical_skills=critical_skills,
        jd_role_family=jd_role["primary"],
        resume_role_family=resume_role["primary"],
        resume_stacks=resume_stacks,
        jd_stacks=jd_stacks,
        evidence_score=evidence_score,
        confidence=confidence,
    )

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
        "resume_feedback": resume_feedback,
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
    return any(not _is_negated_match(normalized_text, match.start()) for match in re.finditer(pattern, normalized_text))


def _is_negated_match(normalized_text: str, start_index: int) -> bool:
    prefix = normalized_text[max(0, start_index - 70):start_index]
    sentence_breaks = [prefix.rfind(";"), prefix.rfind("\n"), prefix.rfind(". ")]
    clause_start = max(sentence_breaks)
    clause = prefix[clause_start + 1:] if clause_start >= 0 else prefix
    tokens = re.findall(r"[a-zA-Z?-?0-9]+", clause.lower())
    if not tokens:
        return False
    joined = " ".join(tokens[-8:])
    return any(term in joined for term in NEGATION_TERMS)


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
    strong_backend_signals = {"backend", "server", "fastapi", "django", "flask", "node.js", "express", "spring", ".net", "asp.net core", "java", "c#"}
    has_strong_backend = any(_contains_skill(normalized, signal) for signal in strong_backend_signals)
    if primary == "backend" and not has_strong_backend:
        if scores.get("mobile", 0) >= 2:
            primary = "mobile"
        elif scores.get("ai/data", 0) >= 2:
            primary = "ai/data"
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
    occurrences = [
        occurrence
        for occurrence in re.finditer(re.escape(_normalize(skill)), normalized)
        if not _is_negated_match(normalized, occurrence.start())
    ]
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
        level = "m\u1ee9c \u0111\u1ed9 ph\u00f9 h\u1ee3p cao"
    elif match_score >= 60:
        level = "m\u1ee9c \u0111\u1ed9 ph\u00f9 h\u1ee3p kh\u00e1"
    elif match_score >= 40:
        level = "m\u1ee9c \u0111\u1ed9 ph\u00f9 h\u1ee3p trung b\u00ecnh"
    else:
        level = "m\u1ee9c \u0111\u1ed9 ph\u00f9 h\u1ee3p c\u00f2n th\u1ea5p"

    matched_text = ", ".join(matched_skills[:5]) if matched_skills else "ch\u01b0a ph\u00e1t hi\u1ec7n k\u1ef9 n\u0103ng tr\u00f9ng kh\u1edbp r\u00f5 r\u00e0ng"
    missing_text = ", ".join(missing_skills[:5]) if missing_skills else "kh\u00f4ng c\u00f3 skill gap l\u1edbn trong danh s\u00e1ch k\u1ef9 n\u0103ng hi\u1ec7n t\u1ea1i"
    semantic_text = (
        f"Semantic score hi\u1ec7n l\u00e0 {semantic_score}/15."
        if semantic_available
        else "Semantic score ch\u01b0a kh\u1ea3 d\u1ee5ng, h\u1ec7 th\u1ed1ng \u0111ang fallback v\u1ec1 rule-based scoring."
    )
    return f"CV c\u00f3 {level} v\u1edbi JD. \u0110i\u1ec3m m\u1ea1nh ch\u00ednh: {matched_text}. Kho\u1ea3ng tr\u1ed1ng c\u1ea7n ch\u00fa \u00fd: {missing_text}. {semantic_text}"

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
        suggestions.append(f"JD \u0111ang y\u00eau c\u1ea7u nhi\u1ec1u k\u1ef9 n\u0103ng CV ch\u01b0a th\u1ec3 hi\u1ec7n r\u00f5. \u01afu ti\u00ean b\u1ed5 sung ho\u1eb7c ch\u1ee9ng minh kinh nghi\u1ec7m v\u1edbi: {top_missing}.")
    elif missing_skills:
        top_missing = ", ".join(missing_skills[:5])
        suggestions.append(f"B\u1ed5 sung ho\u1eb7c l\u00e0m r\u00f5 kinh nghi\u1ec7m li\u00ean quan \u0111\u1ebfn: {top_missing}.")

    if semantic_available and semantic_score < 10:
        suggestions.append("Semantic score th\u1ea5p: n\u00ean vi\u1ebft l\u1ea1i ph\u1ea7n project/experience s\u00e1t JD h\u01a1n, d\u00f9ng m\u00f4 t\u1ea3 tr\u00e1ch nhi\u1ec7m, domain v\u00e0 impact g\u1ea7n v\u1edbi v\u1ecb tr\u00ed m\u1ee5c ti\u00eau.")
    elif semantic_available and semantic_score < 16:
        suggestions.append("Semantic score \u1edf m\u1ee9c trung b\u00ecnh: h\u00e3y l\u00e0m r\u00f5 project n\u00e0o li\u00ean quan tr\u1ef1c ti\u1ebfp \u0111\u1ebfn tr\u00e1ch nhi\u1ec7m trong JD thay v\u00ec ch\u1ec9 li\u1ec7t k\u00ea tech stack.")
    elif not semantic_available:
        suggestions.append("Semantic score ch\u01b0a kh\u1ea3 d\u1ee5ng trong l\u1ea7n ph\u00e2n t\u00edch n\u00e0y; h\u00e3y d\u1ef1a v\u00e0o skill gap, keyword overlap v\u00e0 text preview \u0111\u1ec3 ki\u1ec3m ch\u1ee9ng k\u1ebft qu\u1ea3.")

    suggestions.append("\u0110i\u1ec1u ch\u1ec9nh CV theo JD b\u1eb1ng c\u00e1ch \u0111\u01b0a c\u00e1c keyword quan tr\u1ecdng v\u00e0o ph\u1ea7n project, experience v\u00e0 skills n\u1ebfu ph\u1ea3n \u00e1nh \u0111\u00fang n\u0103ng l\u1ef1c th\u1eadt.")
    if len(resume_text.strip()) < 800:
        suggestions.append("CV \u0111ang kh\u00e1 ng\u1eafn sau khi tr\u00edch xu\u1ea5t text; n\u00ean m\u00f4 t\u1ea3 project b\u1eb1ng impact, tech stack, vai tr\u00f2 c\u00e1 nh\u00e2n v\u00e0 k\u1ebft qu\u1ea3 c\u1ee5 th\u1ec3.")
    if len(job_description_text.strip()) < 300:
        suggestions.append("JD \u0111ang kh\u00e1 ng\u1eafn; k\u1ebft qu\u1ea3 matching s\u1ebd t\u1ed1t h\u01a1n n\u1ebfu JD c\u00f3 \u0111\u1ee7 tr\u00e1ch nhi\u1ec7m, y\u00eau c\u1ea7u k\u1ef9 n\u0103ng v\u00e0 ti\u00eau ch\u00ed \u01b0u ti\u00ean.")
    suggestions.append("\u01afu ti\u00ean c\u1ea3i thi\u1ec7n c\u00e1c skill gap xu\u1ea5t hi\u1ec7n tr\u1ef1c ti\u1ebfp trong JD tr\u01b0\u1edbc khi m\u1edf r\u1ed9ng sang k\u1ef9 n\u0103ng ngo\u00e0i ph\u1ea1m vi v\u1ecb tr\u00ed n\u00e0y.")
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
    role_text = ", ".join(role_context) if role_context != ["general"] else "vai tr\u00f2 m\u1ee5c ti\u00eau"

    if total_missing == 0:
        return "Ch\u01b0a ph\u00e1t hi\u1ec7n skill gap r\u00f5 r\u00e0ng so v\u1edbi JD. CV \u0111ang bao ph\u1ee7 t\u1ed1t c\u00e1c k\u1ef9 n\u0103ng h\u1ec7 th\u1ed1ng nh\u1eadn di\u1ec7n \u0111\u01b0\u1ee3c, n\u00ean \u01b0u ti\u00ean c\u1ea3i thi\u1ec7n c\u00e1ch tr\u00ecnh b\u00e0y cho s\u00e1t JD h\u01a1n."
    if high_count > 0:
        return f"Ph\u00e1t hi\u1ec7n {total_missing} k\u1ef9 n\u0103ng c\u00f2n thi\u1ebfu cho {role_text}, trong \u0111\u00f3 {high_count} k\u1ef9 n\u0103ng thu\u1ed9c nh\u00f3m \u01b0u ti\u00ean cao c\u1ea7n x\u1eed l\u00fd tr\u01b0\u1edbc."
    if medium_count > 0:
        return f"Ph\u00e1t hi\u1ec7n {total_missing} k\u1ef9 n\u0103ng c\u00f2n thi\u1ebfu cho {role_text}. Ch\u01b0a c\u00f3 gap \u01b0u ti\u00ean cao, nh\u01b0ng c\u00f3 {medium_count} k\u1ef9 n\u0103ng n\u00ean l\u00e0m r\u00f5 ho\u1eb7c b\u1ed5 sung."
    return f"Ph\u00e1t hi\u1ec7n {total_missing} k\u1ef9 n\u0103ng c\u00f2n thi\u1ebfu, ch\u1ee7 y\u1ebfu \u1edf m\u1ee9c \u01b0u ti\u00ean th\u1ea5p. CV c\u00f3 th\u1ec3 c\u1ea3i thi\u1ec7n b\u1eb1ng c\u00e1ch alignment t\u1ed1t h\u01a1n v\u1edbi JD."

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
        plan.append(f"C\u00e1c k\u1ef9 n\u0103ng c\u00f2n thi\u1ebfu \u0111ang \u1edf m\u1ee9c \u01b0u ti\u00ean th\u1ea5p ({', '.join(low_priority[:5])}). Ch\u1ec9 b\u1ed5 sung v\u00e0o CV n\u1ebfu b\u1ea1n th\u1ef1c s\u1ef1 \u0111\u00e3 d\u00f9ng trong project ho\u1eb7c kinh nghi\u1ec7m th\u1ef1c t\u1ebf.")

    if not high_priority and not medium_priority and not low_priority:
        plan.append("Gi\u1eef nguy\u00ean skill set ch\u00ednh, nh\u01b0ng vi\u1ebft l\u1ea1i ph\u1ea7n project/experience \u0111\u1ec3 b\u00e1m s\u00e1t ng\u00f4n ng\u1eef trong JD h\u01a1n.")

    if any(skill in high_priority + medium_priority for skill in ("rest api", "api", "database", "postgresql", "sql", "authentication", "jwt")):
        plan.append("Vi\u1ebft l\u1ea1i ph\u1ea7n project \u0111\u1ec3 th\u1ec3 hi\u1ec7n r\u00f5 REST API, database, authentication, vai tr\u00f2 c\u00e1 nh\u00e2n v\u00e0 k\u1ebft qu\u1ea3 \u0111\u1ea1t \u0111\u01b0\u1ee3c.")
    if len(resume_text.strip()) < 800:
        plan.append("CV text \u0111ang ng\u1eafn; b\u1ed5 sung m\u00f4 t\u1ea3 project theo c\u1ea5u tr\u00fac: v\u1ea5n \u0111\u1ec1, tech stack, ph\u1ea7n b\u1ea1n l\u00e0m, k\u1ebft qu\u1ea3 ho\u1eb7c impact.")
    if len(job_description_text.strip()) < 300:
        plan.append("JD \u0111ang ng\u1eafn; n\u1ebfu c\u00f3 th\u1ec3, d\u00f9ng JD \u0111\u1ea7y \u0111\u1ee7 h\u01a1n \u0111\u1ec3 h\u1ec7 th\u1ed1ng ph\u00e2n t\u00edch skill gap ch\u00ednh x\u00e1c h\u01a1n.")

    return _dedupe_preserve_order(plan)[:8]

def _skill_action(skill: str, urgent: bool) -> str:
    prefix = "\u01afu ti\u00ean cao" if urgent else "\u01afu ti\u00ean trung b\u00ecnh"
    if skill == "docker":
        return f"{prefix}: N\u1ebfu \u0111\u00e3 d\u00f9ng Docker, b\u1ed5 sung project ho\u1eb7c kinh nghi\u1ec7m li\u00ean quan. N\u1ebfu ch\u01b0a bi\u1ebft Docker, h\u1ecdc Docker c\u01a1 b\u1ea3n tr\u01b0\u1edbc khi apply v\u1ecb tr\u00ed n\u00e0y."
    if skill in {"rest api", "api"}:
        return f"{prefix}: L\u00e0m r\u00f5 kinh nghi\u1ec7m thi\u1ebft k\u1ebf REST API, endpoint CRUD, validation, error handling v\u00e0 authentication trong project."
    if skill in {"database", "sql", "postgresql", "mysql", "mongodb"}:
        return f"{prefix}: B\u1ed5 sung ph\u1ea7n database: schema, query, relationship, migration ho\u1eb7c t\u1ed1i \u01b0u truy v\u1ea5n n\u1ebfu b\u1ea1n \u0111\u00e3 l\u00e0m."
    if skill in {"authentication", "jwt", "oauth"}:
        return f"{prefix}: Th\u1ec3 hi\u1ec7n r\u00f5 kinh nghi\u1ec7m authentication, JWT/token flow, b\u1ea3o v\u1ec7 endpoint v\u00e0 x\u1eed l\u00fd quy\u1ec1n truy c\u1eadp."
    if skill in {"react", "next.js", "typescript", "javascript", "html", "css", "tailwind"}:
        return f"{prefix}: B\u1ed5 sung v\u00ed d\u1ee5 frontend li\u00ean quan \u0111\u1ebfn {skill}, nh\u1ea5t l\u00e0 component, state, form, API integration v\u00e0 UI production-ready."
    if skill in {"machine learning", "ai", "nlp", "scikit-learn", "pytorch", "tensorflow", "sentence transformers"}:
        return f"{prefix}: B\u1ed5 sung project AI/ML li\u00ean quan \u0111\u1ebfn {skill}, n\u00eau r\u00f5 d\u1eef li\u1ec7u \u0111\u1ea7u v\u00e0o, c\u00e1ch \u0111\u00e1nh gi\u00e1 v\u00e0 k\u1ebft qu\u1ea3."
    return f"{prefix}: B\u1ed5 sung ho\u1eb7c h\u1ecdc n\u1ec1n t\u1ea3ng {skill}; ch\u1ec9 \u0111\u01b0a v\u00e0o CV khi b\u1ea1n c\u00f3 project, b\u00e0i lab ho\u1eb7c kinh nghi\u1ec7m \u0111\u1ee7 ch\u1ee9ng minh."



def _feedback_item(title: str, message: str, why_this_matters: str, suggested_edit: str | None = None) -> dict[str, str]:
    item = {
        "title": title,
        "message": message,
        "why_this_matters": why_this_matters,
    }
    if suggested_edit:
        item["suggested_edit"] = suggested_edit
    return item


def _build_resume_feedback(
    resume_text: str,
    matched_skills: list[str],
    missing_skills: list[str],
    critical_skills: list[str],
    jd_role_family: str,
    resume_role_family: str,
    resume_stacks: list[str],
    jd_stacks: list[str],
    evidence_score: float,
    confidence: str,
) -> dict[str, list[dict[str, str]]]:
    missing_set = set(missing_skills)
    critical_missing = [skill for skill in critical_skills if skill in missing_set]
    weak_matched = [skill for skill in matched_skills if _skill_evidence_level(resume_text, skill)[0] == "weak"]
    evidenced = [skill for skill in matched_skills if _skill_evidence_level(resume_text, skill)[0] in {"medium", "strong"}]

    feedback: dict[str, list[dict[str, str]]] = {
        "critical_gaps": [],
        "cv_wording_improvements": [],
        "suggested_bullet_rewrites": [],
        "missing_evidence_areas": [],
        "recommended_next_edits": [],
    }

    for skill in critical_missing[:5]:
        feedback["critical_gaps"].append(_feedback_item(
            title=f"Missing evidence for {skill}",
            message=f"JD requires {skill}, but the CV does not show clear evidence for it yet.",
            why_this_matters=f"For a {jd_role_family} role, recruiters usually look for proof of role-critical skills, not only adjacent experience.",
            suggested_edit=f"If you actually used {skill}, add it to a project or experience bullet with your specific responsibility.",
        ))

    role_core_missing = [skill for skill in missing_skills if skill in ROLE_CORE_SKILLS.get(jd_role_family, set())]
    for skill in role_core_missing[:4]:
        if skill in critical_missing[:5]:
            continue
        feedback["missing_evidence_areas"].append(_feedback_item(
            title=f"Role-critical keyword missing: {skill}",
            message=f"The JD has {skill}, but the CV does not mention it clearly.",
            why_this_matters=f"{skill} helps the CV look aligned with the target {jd_role_family} responsibilities.",
            suggested_edit=f"If you have real experience with {skill}, add it under the most relevant project instead of only listing it in a skills section.",
        ))

    if evidence_score < 10 or weak_matched:
        important_weak = weak_matched[:5]
        skill_text = ", ".join(important_weak) if important_weak else "the matched skills"
        feedback["cv_wording_improvements"].append(_feedback_item(
            title="Project evidence is still too generic",
            message=f"The CV mentions {skill_text}, but the wording does not strongly prove what you built or owned.",
            why_this_matters="Recruiters need to see technology, responsibility and outcome in the same project bullet.",
            suggested_edit="Rewrite generic bullets with this pattern: Developed [feature] using [tech stack], responsible for [technical task], resulting in [real outcome if you can prove it].",
        ))

    if resume_role_family != jd_role_family and jd_role_family != "general software":
        feedback["recommended_next_edits"].append(_feedback_item(
            title="Role alignment needs to be clearer",
            message=f"The CV currently reads closer to {resume_role_family}, while the JD is closer to {jd_role_family}.",
            why_this_matters="A role mismatch can make relevant transferable work harder for recruiters to notice.",
            suggested_edit=f"Move the most relevant {jd_role_family} project or technical responsibility higher in the CV if you have it.",
        ))

    if jd_stacks and not set(resume_stacks).intersection(jd_stacks):
        feedback["recommended_next_edits"].append(_feedback_item(
            title="Stack gap should be handled explicitly",
            message=f"JD stack signals include {', '.join(jd_stacks[:4])}, but the CV stack signals are {', '.join(resume_stacks[:4]) or 'not clear'}.",
            why_this_matters="Same-role candidates can still be screened out when the target stack is not visible.",
            suggested_edit="If you have used the JD stack, add it with project evidence. If not, position your current stack as transferable and prioritize learning the missing stack.",
        ))

    feedback["suggested_bullet_rewrites"].extend(_suggest_safe_bullet_rewrites(evidenced, jd_role_family)[:3])

    if confidence == "low":
        feedback["recommended_next_edits"].append(_feedback_item(
            title="CV text is not enough for confident feedback",
            message="The extracted CV text or detected evidence is limited, so suggestions should be checked against the original CV.",
            why_this_matters="Low extraction quality can make the system miss real experience.",
            suggested_edit="Verify the CV preview first, then add more detailed project bullets if important content is missing.",
        ))

    if not any(feedback.values()):
        feedback["recommended_next_edits"].append(_feedback_item(
            title="CV is already aligned on detected skills",
            message="No major rewrite issue was detected from the current CV and JD text.",
            why_this_matters="For a strong fit, the next improvement is usually clarity and ordering rather than adding unsupported claims.",
            suggested_edit="Keep the most relevant project near the top and make sure each bullet shows tech stack, responsibility and real outcome.",
        ))

    return feedback


def _suggest_safe_bullet_rewrites(evidenced_skills: list[str], jd_role_family: str) -> list[dict[str, str]]:
    skill_set = set(evidenced_skills)
    suggestions = []
    role_templates = {
        "backend": [
            ({"api", "rest api", "authentication", "jwt"}, "Developed backend REST API workflows with authentication/JWT support and clear request validation."),
            ({"database", "sql", "postgresql"}, "Implemented database-backed features using SQL/PostgreSQL and documented schema or query responsibilities."),
            ({"docker"}, "If you actually handled deployment, describe how Docker was used to run or package the backend service."),
            ({"c#", ".net", "asp.net core"}, "Developed ASP.NET Core backend APIs for core workflows, including validation, data access and service logic."),
            ({"python", "fastapi"}, "Developed FastAPI backend endpoints for core workflows, including validation, data access and service logic."),
        ],
        "frontend": [
            ({"react", "typescript", "javascript"}, "Built React/TypeScript UI components and integrated them with backend APIs and user-facing states."),
            ({"html", "css", "tailwind"}, "Implemented responsive UI screens with HTML/CSS/Tailwind and handled loading, empty and error states."),
            ({"api", "rest api", "authentication"}, "Integrated frontend screens with REST APIs and authentication state for a production-style user flow."),
        ],
        "ai/data": [
            ({"python", "machine learning", "scikit-learn"}, "Built Python machine learning experiments with clear dataset preparation, model evaluation and result interpretation."),
            ({"pandas", "numpy", "sql"}, "Prepared and analyzed datasets using pandas/numpy/SQL, then documented the insight or decision supported by the analysis."),
        ],
    }
    templates = role_templates.get(jd_role_family, []) + role_templates.get("backend", [])[:1]
    for required_skills, rewrite in templates:
        if required_skills.intersection(skill_set):
            suggestions.append(_feedback_item(
                title="Safe bullet rewrite template",
                message="Use this only if it accurately reflects what you implemented.",
                why_this_matters="This turns a generic project line into a recruiter-readable technical responsibility.",
                suggested_edit=rewrite,
            ))
    if not suggestions and evidenced_skills:
        suggestions.append(_feedback_item(
            title="Make evidenced skills more specific",
            message=f"The CV has evidence for {', '.join(evidenced_skills[:4])}, but the strongest bullet can be more explicit.",
            why_this_matters="Specific bullets are easier to match with JD requirements than broad claims.",
            suggested_edit="Rewrite one project bullet to include the feature, tech stack, your responsibility and a real outcome if available.",
        ))
    return _dedupe_feedback_items(suggestions)


def _dedupe_feedback_items(items: list[dict[str, str]]) -> list[dict[str, str]]:
    seen = set()
    deduped = []
    for item in items:
        key = (item.get("title"), item.get("message"), item.get("suggested_edit"))
        if key not in seen:
            deduped.append(item)
            seen.add(key)
    return deduped


def _dedupe_preserve_order(items: list[str]) -> list[str]:
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            result.append(item)
            seen.add(item)
    return result











