from app.models.career_profile import CareerProfile
from app.services.resume_job_matcher import extract_skills

QUESTION_COUNT = 5

QUESTION_BANK = {
    "backend": [
        {"question": "REST API là gì và bạn sẽ thiết kế endpoint CRUD như thế nào?", "keywords": ["rest api", "http", "crud", "endpoint", "status code", "validation"]},
        {"question": "JWT hoạt động như thế nào trong authentication flow?", "keywords": ["jwt", "token", "login", "signature", "expire", "authorization"]},
        {"question": "Bạn thiết kế database PostgreSQL cho một feature mới như thế nào?", "keywords": ["postgresql", "schema", "relationship", "query", "index", "migration"]},
        {"question": "Bạn xử lý validation và error handling trong FastAPI/API backend ra sao?", "keywords": ["validation", "error handling", "fastapi", "pydantic", "exception", "response"]},
        {"question": "Docker giúp gì khi deploy backend và bạn thường cấu hình những gì?", "keywords": ["docker", "container", "image", "environment", "deploy", "port"]},
    ],
    "frontend": [
        {"question": "Bạn tổ chức component React cho một form có API call như thế nào?", "keywords": ["react", "component", "state", "form", "api", "validation"]},
        {"question": "Next.js hỗ trợ routing và rendering như thế nào?", "keywords": ["next.js", "routing", "server", "client", "rendering", "page"]},
        {"question": "Bạn xử lý authentication token ở frontend như thế nào?", "keywords": ["token", "jwt", "localStorage", "authorization", "protected route", "logout"]},
        {"question": "Làm sao để UI responsive và dễ maintain với Tailwind CSS?", "keywords": ["tailwind", "responsive", "grid", "flex", "breakpoint", "component"]},
        {"question": "TypeScript giúp giảm lỗi trong frontend như thế nào?", "keywords": ["typescript", "type", "interface", "props", "api response", "compile"]},
    ],
    "fullstack": [
        {"question": "Mô tả flow từ form frontend tới backend API và database.", "keywords": ["frontend", "backend", "api", "database", "request", "response"]},
        {"question": "Bạn thiết kế authentication end-to-end bằng JWT như thế nào?", "keywords": ["jwt", "login", "token", "protected route", "authorization", "backend"]},
        {"question": "Khi API trả lỗi, bạn xử lý trải nghiệm người dùng ở frontend ra sao?", "keywords": ["error", "validation", "message", "state", "fallback", "retry"]},
        {"question": "Bạn deploy frontend và backend riêng nhau cần chú ý gì?", "keywords": ["deploy", "vercel", "render", "environment", "cors", "api url"]},
        {"question": "Bạn sẽ debug một bug dữ liệu sai từ UI tới database như thế nào?", "keywords": ["debug", "log", "network", "payload", "database", "api"]},
    ],
    "ai": [
        {"question": "Bạn giải thích machine learning pipeline đơn giản gồm những bước nào?", "keywords": ["machine learning", "data", "feature", "model", "train", "evaluate"]},
        {"question": "Semantic similarity là gì và khi nào nên dùng Sentence Transformers?", "keywords": ["semantic", "similarity", "sentence transformers", "embedding", "cosine", "text"]},
        {"question": "Bạn đánh giá một mô hình phân loại cơ bản bằng metric nào?", "keywords": ["metric", "accuracy", "precision", "recall", "f1", "validation"]},
        {"question": "Rule-based và ML-based approach khác nhau như thế nào?", "keywords": ["rule-based", "machine learning", "data", "explainable", "fallback", "model"]},
        {"question": "Bạn xử lý text preprocessing cho bài toán NLP như thế nào?", "keywords": ["nlp", "token", "normalize", "stopwords", "embedding", "text"]},
    ],
    "general": [
        {"question": "Hãy giới thiệu một project công nghệ bạn đã làm và vai trò của bạn.", "keywords": ["project", "role", "tech stack", "problem", "solution", "result"]},
        {"question": "Khi gặp bug khó, bạn thường debug theo quy trình nào?", "keywords": ["debug", "reproduce", "log", "root cause", "fix", "test"]},
        {"question": "Bạn học một công nghệ mới như thế nào để áp dụng vào project thật?", "keywords": ["learn", "documentation", "practice", "project", "example", "apply"]},
        {"question": "Bạn đảm bảo code dễ maintain bằng những nguyên tắc nào?", "keywords": ["clean code", "naming", "validation", "error handling", "test", "structure"]},
        {"question": "Bạn chuẩn bị CV theo Job Description mục tiêu như thế nào?", "keywords": ["cv", "job description", "skill", "project", "keyword", "impact"]},
    ],
}

SKILL_QUESTIONS = {
    "docker": {"question": "Docker giải quyết vấn đề gì trong quá trình build/deploy application?", "keywords": ["docker", "container", "image", "environment", "deploy", "volume"]},
    "jwt": {"question": "JWT gồm những phần nào và backend nên verify token ra sao?", "keywords": ["jwt", "header", "payload", "signature", "verify", "expire"]},
    "authentication": {"question": "Bạn thiết kế authentication flow cho user login như thế nào?", "keywords": ["authentication", "login", "password", "token", "authorization", "protected"]},
    "rest api": {"question": "Một REST API tốt cần chú ý những yếu tố nào?", "keywords": ["rest api", "resource", "method", "status code", "validation", "error"]},
    "postgresql": {"question": "Bạn dùng PostgreSQL để thiết kế dữ liệu quan hệ như thế nào?", "keywords": ["postgresql", "table", "relationship", "query", "index", "constraint"]},
    "react": {"question": "React state và props khác nhau như thế nào trong component?", "keywords": ["react", "state", "props", "component", "render", "event"]},
    "next.js": {"question": "Next.js khác React thuần ở những điểm nào khi xây product?", "keywords": ["next.js", "routing", "server", "client", "rendering", "deployment"]},
    "typescript": {"question": "TypeScript giúp bạn bắt lỗi API response hoặc props như thế nào?", "keywords": ["typescript", "type", "interface", "props", "api", "compile"]},
    "machine learning": {"question": "Bạn sẽ xây MVP machine learning đơn giản như thế nào trước khi nghĩ đến model phức tạp?", "keywords": ["machine learning", "data", "baseline", "metric", "evaluate", "model"]},
    "nlp": {"question": "Trong NLP, bạn preprocessing text trước khi matching hoặc embedding như thế nào?", "keywords": ["nlp", "text", "normalize", "token", "embedding", "similarity"]},
}


def generate_interview_questions(target_role: str, missing_skills: list[str] | None = None) -> list[dict[str, object]]:
    role_key = detect_role_key(target_role)
    questions: list[dict[str, object]] = []

    for skill in missing_skills or []:
        normalized_skill = skill.strip().lower()
        if normalized_skill in SKILL_QUESTIONS:
            questions.append(SKILL_QUESTIONS[normalized_skill])

    for question in QUESTION_BANK.get(role_key, QUESTION_BANK["general"]):
        questions.append(question)
    for question in QUESTION_BANK["general"]:
        questions.append(question)

    return _dedupe_questions(questions)[:QUESTION_COUNT]


def detect_role_key(target_role: str) -> str:
    normalized = (target_role or "").lower()
    if any(token in normalized for token in ("fullstack", "full-stack", "full stack")):
        return "fullstack"
    if any(token in normalized for token in ("backend", "back-end", "api", "server")):
        return "backend"
    if any(token in normalized for token in ("frontend", "front-end", "react", "next")):
        return "frontend"
    if any(token in normalized for token in ("ai", "machine learning", "ml", "nlp", "data")):
        return "ai"
    return "general"


def infer_target_role(profile: CareerProfile | None, explicit_target_role: str | None) -> str:
    if explicit_target_role and explicit_target_role.strip():
        return explicit_target_role.strip()
    if profile and profile.target_role.strip():
        return profile.target_role.strip()
    return "General Software Developer"


def infer_profile_skills(profile: CareerProfile | None) -> list[str]:
    if profile is None:
        return []
    return extract_skills(" ".join([profile.skills, profile.projects_summary, profile.experience_summary]))


def _dedupe_questions(questions: list[dict[str, object]]) -> list[dict[str, object]]:
    seen = set()
    result = []
    for question in questions:
        text = str(question["question"])
        if text not in seen:
            result.append(question)
            seen.add(text)
    return result