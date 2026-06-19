from typing import Any

from app.ai.taxonomy_insights import normalize_skill_list, normalize_skill_name
from app.models.career_profile import CareerProfile
from app.services.resume_job_matcher import extract_skills

QUESTION_COUNT = 5

Question = dict[str, object]


CATEGORY_HINTS = {
    "concept": "N\u00ean tr\u1ea3 l\u1eddi theo c\u1ea5u tr\u00fac: kh\u00e1i ni\u1ec7m, c\u00e1ch ho\u1ea1t \u0111\u1ed9ng, v\u00ed d\u1ee5 ng\u1eafn.",
    "project_evidence": "N\u00ean g\u1eafn c\u00e2u tr\u1ea3 l\u1eddi v\u1edbi project th\u1eadt: b\u1ea1n l\u00e0m g\u00ec, d\u00f9ng tech n\u00e0o, output l\u00e0 g\u00ec.",
    "debugging": "N\u00ean n\u00f3i quy tr\u00ecnh debug: reproduce, xem log, khoanh v\u00f9ng nguy\u00ean nh\u00e2n, fix v\u00e0 test l\u1ea1i.",
    "tradeoff": "N\u00ean n\u00eau l\u1ef1a ch\u1ecdn, khi n\u00e0o d\u00f9ng, khi n\u00e0o kh\u00f4ng d\u00f9ng v\u00e0 v\u00ec sao.",
    "behavioral_lite": "N\u00ean tr\u1ea3 l\u1eddi ng\u1eafn g\u1ecdn, c\u00f3 context, action v\u00e0 b\u00e0i h\u1ecdc r\u00fat ra.",
}


def q(question: str, keywords: list[str], category: str, reason: str, related_skills: list[str], stack_group: str) -> Question:
    return {
        "question": question,
        "keywords": keywords,
        "category": category,
        "reason": reason,
        "related_skills": related_skills,
        "stack_group": stack_group,
        "better_answer_hint": CATEGORY_HINTS.get(category, CATEGORY_HINTS["behavioral_lite"]),
    }


QUESTION_BANK: dict[str, list[Question]] = {
    "backend_dotnet": [
        q("JWT ho\u1ea1t \u0111\u1ed9ng nh\u01b0 th\u1ebf n\u00e0o trong m\u1ed9t ASP.NET Core Web API?", ["jwt", "token", "signature", "authorization", "middleware", "expire"], "concept", "C\u00e2u n\u00e0y ki\u1ec3m tra n\u1ec1n t\u1ea3ng authentication cho Backend .NET.", ["jwt", "authentication", "asp.net core"], "backend_dotnet"),
        q("Khi n\u00e0o n\u00ean d\u00f9ng DTO thay v\u00ec tr\u1ea3 Entity tr\u1ef1c ti\u1ebfp t\u1eeb API?", ["dto", "entity", "api", "security", "validation", "mapping"], "tradeoff", "Backend .NET th\u01b0\u1eddng c\u1ea7n gi\u1ea3i th\u00edch r\u00f5 boundary gi\u1eefa API contract v\u00e0 database model.", ["asp.net core", "api", "database"], "backend_dotnet"),
        q("B\u1ea1n x\u1eed l\u00fd validation v\u00e0 error response trong API nh\u01b0 th\u1ebf n\u00e0o?", ["validation", "error", "status code", "response", "modelstate", "exception"], "debugging", "C\u00e2u n\u00e0y \u0111\u00e1nh gi\u00e1 kh\u1ea3 n\u0103ng l\u00e0m API production-ready.", ["api", "validation", "error handling"], "backend_dotnet"),
        q("EF Core Include v\u00e0 AsNoTracking n\u00ean d\u00f9ng khi n\u00e0o?", ["ef core", "include", "asnotracking", "query", "performance", "relationship"], "concept", "JD .NET th\u01b0\u1eddng y\u00eau c\u1ea7u ORM/database, n\u00ean c\u00e2u n\u00e0y ki\u1ec3m tra hi\u1ec3u bi\u1ebft EF Core c\u01a1 b\u1ea3n.", ["ef core", "database", "sql"], "backend_dotnet"),
        q("M\u00f4 t\u1ea3 m\u1ed9t endpoint b\u1ea1n \u0111\u00e3 x\u00e2y d\u1ef1ng t\u1eeb request \u0111\u1ebfn database.", ["endpoint", "request", "validation", "service", "database", "response"], "project_evidence", "C\u00e2u n\u00e0y bu\u1ed9c b\u1ea1n ch\u1ee9ng minh kinh nghi\u1ec7m project thay v\u00ec ch\u1ec9 n\u00f3i l\u00fd thuy\u1ebft.", ["api", "database", "backend"], "backend_dotnet"),
    ],
    "backend_node": [
        q("B\u1ea1n t\u1ed5 ch\u1ee9c route, controller v\u00e0 service trong Node.js/Express nh\u01b0 th\u1ebf n\u00e0o?", ["node.js", "express", "route", "controller", "service", "middleware"], "project_evidence", "C\u00e2u n\u00e0y ki\u1ec3m tra c\u00e1ch b\u1ea1n t\u1ed5 ch\u1ee9c backend Node.js c\u00f3 maintainability.", ["node.js", "express", "api"], "backend_node"),
        q("Middleware trong Express d\u00f9ng \u0111\u1ec3 l\u00e0m g\u00ec?", ["middleware", "request", "response", "next", "auth", "error"], "concept", "Middleware l\u00e0 ph\u1ea7n c\u1ed1t l\u00f5i khi x\u1eed l\u00fd auth, logging v\u00e0 error trong Express.", ["express", "middleware"], "backend_node"),
        q("B\u1ea1n validate input v\u00e0 tr\u1ea3 l\u1ed7i API trong Node.js nh\u01b0 th\u1ebf n\u00e0o?", ["validation", "error", "schema", "status code", "response", "api"], "debugging", "C\u00e2u n\u00e0y b\u00e1m v\u00e0o quality c\u1ee7a API ch\u1ee9 kh\u00f4ng ch\u1ec9 syntax.", ["api", "validation", "node.js"], "backend_node"),
        q("Khi n\u00e0o b\u1ea1n t\u00e1ch business logic kh\u1ecfi controller?", ["controller", "service", "business logic", "test", "maintain", "separation"], "tradeoff", "C\u00e2u n\u00e0y ki\u1ec3m tra kh\u1ea3 n\u0103ng thi\u1ebft k\u1ebf code backend d\u1ec5 maintain.", ["backend", "architecture"], "backend_node"),
    ],
    "backend_python": [
        q("FastAPI dependency injection h\u1ed7 tr\u1ee3 auth ho\u1eb7c database session nh\u01b0 th\u1ebf n\u00e0o?", ["fastapi", "dependency", "auth", "database", "session", "request"], "concept", "C\u00e2u n\u00e0y ph\u00f9 h\u1ee3p v\u1edbi Backend Python/FastAPI v\u00e0 c\u00e1c API c\u1ea7n JWT/database.", ["fastapi", "python", "database"], "backend_python"),
        q("Pydantic gi\u00fap validation request/response trong FastAPI nh\u01b0 th\u1ebf n\u00e0o?", ["pydantic", "validation", "schema", "request", "response", "type"], "concept", "Validation l\u00e0 skill quan tr\u1ecdng cho API production-ready.", ["fastapi", "validation"], "backend_python"),
        q("B\u1ea1n thi\u1ebft k\u1ebf m\u1ed9t REST API nh\u1ecf b\u1eb1ng FastAPI t\u1eeb route \u0111\u1ebfn database nh\u01b0 th\u1ebf n\u00e0o?", ["rest api", "fastapi", "route", "database", "sqlalchemy", "response"], "project_evidence", "C\u00e2u n\u00e0y y\u00eau c\u1ea7u b\u1ea1n n\u00f3i t\u1eeb project/evidence th\u1eadt.", ["fastapi", "rest api", "database"], "backend_python"),
        q("Khi API b\u1ecb l\u1ed7i 500, b\u1ea1n debug theo th\u1ee9 t\u1ef1 n\u00e0o?", ["debug", "log", "traceback", "request", "database", "exception"], "debugging", "Debugging l\u00e0 n\u0103ng l\u1ef1c th\u1ef1c t\u1ebf quan tr\u1ecdng cho backend intern/junior.", ["debugging", "backend"], "backend_python"),
    ],
    "frontend_react": [
        q("Component controlled v\u00e0 uncontrolled trong React kh\u00e1c nhau nh\u01b0 th\u1ebf n\u00e0o?", ["react", "controlled", "uncontrolled", "state", "form", "input"], "concept", "C\u00e2u n\u00e0y ki\u1ec3m tra n\u1ec1n t\u1ea3ng form/state trong React.", ["react", "form", "state"], "frontend_react"),
        q("B\u1ea1n x\u1eed l\u00fd loading, error v\u00e0 empty state trong UI nh\u01b0 th\u1ebf n\u00e0o?", ["loading", "error", "empty", "state", "ui", "retry"], "debugging", "Product UI c\u1ea7n state r\u00f5 r\u00e0ng, \u0111\u00e2y l\u00e0 skill quan tr\u1ecdng cho frontend.", ["react", "ui", "state"], "frontend_react"),
        q("Khi t\u00edch h\u1ee3p REST API, b\u1ea1n t\u1ed5 ch\u1ee9c service layer \u1edf frontend ra sao?", ["rest api", "service", "fetch", "error", "type", "token"], "project_evidence", "C\u00e2u n\u00e0y b\u00e1m v\u00e0o kinh nghi\u1ec7m t\u00edch h\u1ee3p frontend-backend th\u1eadt.", ["react", "rest api", "typescript"], "frontend_react"),
        q("L\u00e0m sao \u0111\u1ec3 tr\u00e1nh prop drilling trong React?", ["prop drilling", "context", "state", "component", "composition", "store"], "tradeoff", "C\u00e2u n\u00e0y ki\u1ec3m tra kh\u1ea3 n\u0103ng ch\u1ecdn state management v\u1eeba \u0111\u1ee7, kh\u00f4ng over-engineer.", ["react", "state"], "frontend_react"),
        q("M\u00f4 t\u1ea3 m\u1ed9t m\u00e0n h\u00ecnh b\u1ea1n \u0111\u00e3 x\u00e2y d\u1ef1ng v\u00e0 c\u00e1c state ch\u00ednh c\u1ee7a n\u00f3.", ["screen", "state", "loading", "error", "form", "api"], "project_evidence", "C\u00e2u n\u00e0y gi\u00fap b\u1ea1n k\u1ec3 evidence t\u1eeb project thay v\u00ec n\u00f3i chung chung.", ["react", "ui", "project"], "frontend_react"),
    ],
    "ai_data": [
        q("Train/test split l\u00e0 g\u00ec v\u00e0 v\u00ec sao kh\u00f4ng n\u00ean \u0111\u00e1nh gi\u00e1 model tr\u00ean train data?", ["train", "test", "split", "evaluation", "data leakage", "model"], "concept", "C\u00e2u n\u00e0y ki\u1ec3m tra n\u1ec1n t\u1ea3ng ML evaluation c\u01a1 b\u1ea3n.", ["machine learning", "evaluation"], "ai_data"),
        q("Precision, recall v\u00e0 F1-score kh\u00e1c nhau nh\u01b0 th\u1ebf n\u00e0o?", ["precision", "recall", "f1", "false positive", "false negative", "metric"], "concept", "AI/Data role c\u1ea7n gi\u1ea3i th\u00edch metric theo b\u00e0i to\u00e1n.", ["machine learning", "metric"], "ai_data"),
        q("B\u1ea1n x\u1eed l\u00fd d\u1eef li\u1ec7u thi\u1ebfu trong dataset nh\u01b0 th\u1ebf n\u00e0o?", ["missing data", "impute", "drop", "feature", "pandas", "quality"], "debugging", "D\u1eef li\u1ec7u b\u1ea9n l\u00e0 case th\u1ef1c t\u1ebf th\u01b0\u1eddng g\u1eb7p trong AI/Data.", ["pandas", "data", "feature"], "ai_data"),
        q("Overfitting l\u00e0 g\u00ec v\u00e0 c\u00f3 th\u1ec3 gi\u1ea3m b\u1eb1ng c\u00e1ch n\u00e0o?", ["overfitting", "regularization", "validation", "data", "model", "generalization"], "tradeoff", "C\u00e2u n\u00e0y ki\u1ec3m tra kh\u1ea3 n\u0103ng nh\u1eadn bi\u1ebft risk khi model qu\u00e1 kh\u1edbp train data.", ["machine learning", "model"], "ai_data"),
        q("M\u00f4 t\u1ea3 m\u1ed9t pipeline ML \u0111\u01a1n gi\u1ea3n t\u1eeb data \u0111\u1ebfn evaluation.", ["data", "preprocess", "feature", "model", "train", "evaluate"], "project_evidence", "C\u00e2u n\u00e0y y\u00eau c\u1ea7u b\u1ea1n k\u1ebft n\u1ed1i l\u00fd thuy\u1ebft v\u1edbi project/pipeline th\u1eadt.", ["machine learning", "pipeline"], "ai_data"),
    ],
    "mobile_flutter": [
        q("StatefulWidget v\u00e0 StatelessWidget kh\u00e1c nhau nh\u01b0 th\u1ebf n\u00e0o trong Flutter?", ["flutter", "statefulwidget", "statelesswidget", "state", "widget", "build"], "concept", "C\u00e2u n\u00e0y ki\u1ec3m tra n\u1ec1n t\u1ea3ng UI/state trong Flutter.", ["flutter", "state"], "mobile_flutter"),
        q("B\u1ea1n t\u00edch h\u1ee3p REST API trong Flutter app nh\u01b0 th\u1ebf n\u00e0o?", ["flutter", "rest api", "http", "json", "loading", "error"], "project_evidence", "Mobile role c\u1ea7n ch\u1ee9ng minh lu\u1ed3ng app g\u1ecdi API th\u1eadt.", ["flutter", "rest api"], "mobile_flutter"),
        q("Khi app b\u1ecb crash ho\u1eb7c UI render sai, b\u1ea1n debug th\u1ebf n\u00e0o?", ["debug", "log", "state", "widget", "error", "reproduce"], "debugging", "Debugging l\u00e0 skill quan tr\u1ecdng trong mobile development.", ["flutter", "debugging"], "mobile_flutter"),
        q("B\u1ea1n qu\u1ea3n l\u00fd navigation v\u00e0 form state trong Flutter nh\u01b0 th\u1ebf n\u00e0o?", ["navigation", "form", "state", "validation", "route", "controller"], "tradeoff", "C\u00e2u n\u00e0y b\u00e1m v\u00e0o workflow mobile app th\u1ef1c t\u1ebf.", ["flutter", "form"], "mobile_flutter"),
    ],
    "general": [
        q("H\u00e3y gi\u1edbi thi\u1ec7u m\u1ed9t project c\u00f4ng ngh\u1ec7 b\u1ea1n \u0111\u00e3 l\u00e0m v\u00e0 vai tr\u00f2 c\u1ee7a b\u1ea1n.", ["project", "role", "tech stack", "problem", "solution", "result"], "behavioral_lite", "C\u00e2u n\u00e0y gi\u00fap \u0111\u00e1nh gi\u00e1 kh\u1ea3 n\u0103ng k\u1ec3 project evidence c\u01a1 b\u1ea3n.", ["project", "communication"], "general"),
        q("Khi g\u1eb7p bug kh\u00f3, b\u1ea1n debug theo quy tr\u00ecnh n\u00e0o?", ["debug", "reproduce", "log", "root cause", "fix", "test"], "debugging", "C\u00e2u n\u00e0y ph\u00f9 h\u1ee3p cho intern/junior \u1edf h\u1ea7u h\u1ebft role software.", ["debugging"], "general"),
        q("B\u1ea1n chu\u1ea9n b\u1ecb CV theo JD m\u1ee5c ti\u00eau nh\u01b0 th\u1ebf n\u00e0o?", ["cv", "jd", "skill", "project", "keyword", "evidence"], "behavioral_lite", "C\u00e2u n\u00e0y ki\u1ec3m tra t\u01b0 duy alignment CV/JD m\u00e0 CareerOS AI \u0111ang h\u1ed7 tr\u1ee3.", ["cv", "jd"], "general"),
    ],
}

SKILL_QUESTIONS: dict[str, Question] = {
    "jwt": q("JWT ho\u1ea1t \u0111\u1ed9ng nh\u01b0 th\u1ebf n\u00e0o v\u00e0 b\u1ea1n s\u1ebd b\u1ea3o v\u1ec7 endpoint b\u1eb1ng token ra sao?", ["jwt", "token", "signature", "expire", "authorization", "protected endpoint"], "concept", "C\u00e2u n\u00e0y \u0111\u01b0\u1ee3c \u01b0u ti\u00ean v\u00ec JWT l\u00e0 skill gap ho\u1eb7c critical skill trong analysis.", ["jwt", "authentication"], "backend"),
    "authentication": q("B\u1ea1n thi\u1ebft k\u1ebf authentication flow cho user login nh\u01b0 th\u1ebf n\u00e0o?", ["authentication", "login", "password", "token", "authorization", "protected"], "concept", "Authentication th\u01b0\u1eddng l\u00e0 skill c\u1ed1t l\u00f5i trong JD backend/fullstack.", ["authentication", "jwt"], "backend"),
    "asp.net core": q("Trong ASP.NET Core, middleware v\u00e0 dependency injection h\u1ed7 tr\u1ee3 API nh\u01b0 th\u1ebf n\u00e0o?", ["asp.net core", "middleware", "dependency injection", "service", "api", "request"], "concept", "C\u00e2u n\u00e0y b\u00e1m v\u00e0o stack .NET m\u00e0 JD y\u00eau c\u1ea7u.", ["asp.net core", ".net"], "backend_dotnet"),
    "c#": q("C# \u0111\u01b0\u1ee3c d\u00f9ng trong backend .NET project c\u1ee7a b\u1ea1n nh\u01b0 th\u1ebf n\u00e0o?", ["c#", ".net", "class", "service", "api", "project"], "project_evidence", "C\u00e2u n\u00e0y ki\u1ec3m tra evidence th\u1eadt n\u1ebfu JD y\u00eau c\u1ea7u .NET/C#.", ["c#", ".net"], "backend_dotnet"),
    "react": q("M\u00f4 t\u1ea3 m\u1ed9t React component b\u1ea1n \u0111\u00e3 x\u00e2y d\u1ef1ng v\u00e0 c\u00e1ch n\u00f3 qu\u1ea3n l\u00fd state.", ["react", "component", "state", "props", "ui", "api"], "project_evidence", "C\u00e2u n\u00e0y \u0111\u01b0\u1ee3c \u01b0u ti\u00ean khi React l\u00e0 missing skill ho\u1eb7c critical skill.", ["react", "state"], "frontend_react"),
    "rest api": q("M\u1ed9t REST API t\u1ed1t c\u1ea7n ch\u00fa \u00fd nh\u1eefng y\u1ebfu t\u1ed1 n\u00e0o?", ["rest api", "resource", "method", "status code", "validation", "error"], "concept", "REST API l\u00e0 skill giao thoa quan tr\u1ecdng gi\u1eefa backend v\u00e0 frontend integration.", ["rest api", "api"], "backend"),
    "docker": q("Docker gi\u00fap g\u00ec trong qu\u00e1 tr\u00ecnh build/deploy application?", ["docker", "container", "image", "environment", "deploy", "port"], "tradeoff", "Docker th\u01b0\u1eddng l\u00e0 gap tri\u1ec3n khai/deployment trong JD backend.", ["docker", "deployment"], "devops"),
    "postgresql": q("B\u1ea1n thi\u1ebft k\u1ebf schema PostgreSQL cho m\u1ed9t feature th\u1ef1c t\u1ebf nh\u01b0 th\u1ebf n\u00e0o?", ["postgresql", "schema", "relationship", "query", "index", "constraint"], "project_evidence", "C\u00e2u n\u00e0y ki\u1ec3m tra database evidence khi JD y\u00eau c\u1ea7u SQL/PostgreSQL.", ["postgresql", "sql", "database"], "backend"),
    "machine learning": q("M\u00f4 t\u1ea3 m\u1ed9t pipeline ML \u0111\u01a1n gi\u1ea3n v\u00e0 c\u00e1ch b\u1ea1n \u0111\u00e1nh gi\u00e1 k\u1ebft qu\u1ea3.", ["machine learning", "data", "train", "evaluate", "metric", "model"], "project_evidence", "C\u00e2u n\u00e0y \u0111\u01b0\u1ee3c \u01b0u ti\u00ean khi AI/Data l\u00e0 role ho\u1eb7c skill gap.", ["machine learning", "evaluation"], "ai_data"),
    "flutter": q("B\u1ea1n x\u00e2y m\u1ed9t m\u00e0n h\u00ecnh Flutter c\u00f3 state v\u00e0 API call nh\u01b0 th\u1ebf n\u00e0o?", ["flutter", "state", "api", "widget", "loading", "error"], "project_evidence", "C\u00e2u n\u00e0y b\u00e1m v\u00e0o evidence mobile app th\u1eadt.", ["flutter", "mobile"], "mobile_flutter"),
}


def generate_interview_questions(
    target_role: str,
    missing_skills: list[str] | None = None,
    roadmap_items: list[dict[str, Any]] | None = None,
    analysis_context: dict[str, Any] | None = None,
) -> list[Question]:
    role_key = detect_role_key(target_role, analysis_context=analysis_context)
    critical_skills = normalize_skill_list(_as_list((analysis_context or {}).get("critical_skills")))
    prioritized_skills = normalize_skill_list(_dedupe([*critical_skills, *(missing_skills or [])]))
    questions: list[Question] = []

    for skill in prioritized_skills:
        normalized_skill = normalize_skill_name(skill).lower()
        if normalized_skill in SKILL_QUESTIONS:
            questions.append(_with_reason(SKILL_QUESTIONS[normalized_skill], "C\u00e2u n\u00e0y \u0111\u01b0\u1ee3c \u01b0u ti\u00ean v\u00ec skill n\u00e0y \u0111ang thi\u1ebfu ho\u1eb7c l\u00e0 critical skill trong JD."))

    questions.extend(_questions_from_roadmap(roadmap_items or []))
    questions.extend(QUESTION_BANK.get(role_key, QUESTION_BANK["general"]))
    if role_key != "general":
        questions.extend(QUESTION_BANK["general"])

    return _dedupe_questions(questions)[:QUESTION_COUNT]


def detect_role_key(target_role: str, analysis_context: dict[str, Any] | None = None) -> str:
    normalized_context_skills = " ".join(normalize_skill_list(_as_list((analysis_context or {}).get("critical_skills"))))
    normalized = " ".join([target_role or "", " ".join(_as_list((analysis_context or {}).get("stack_groups"))), normalized_context_skills]).lower()
    if any(token in normalized for token in ("asp.net", ".net", "dotnet", "c#", "ef core")):
        return "backend_dotnet"
    if any(token in normalized for token in ("node", "express", "nestjs")):
        return "backend_node"
    if any(token in normalized for token in ("fastapi", "django", "flask", "python backend")):
        return "backend_python"
    if any(token in normalized for token in ("react", "next.js", "nextjs", "frontend")):
        return "frontend_react"
    if any(token in normalized for token in ("flutter", "mobile")):
        return "mobile_flutter"
    if any(token in normalized for token in ("ai", "machine learning", "ml", "nlp", "data")):
        return "ai_data"
    if any(token in normalized for token in ("backend", "api", "server")):
        return "backend_python"
    return "general"


def infer_target_role(profile: CareerProfile | None, explicit_target_role: str | None) -> str:
    if explicit_target_role and explicit_target_role.strip():
        return explicit_target_role.strip()
    if profile and profile.target_role.strip():
        return profile.target_role.strip()
    return "General Software Intern"


def infer_profile_skills(profile: CareerProfile | None) -> list[str]:
    if profile is None:
        return []
    return normalize_skill_list(extract_skills(" ".join([profile.skills, profile.projects_summary, profile.experience_summary])))


def _questions_from_roadmap(items: list[dict[str, Any]]) -> list[Question]:
    result: list[Question] = []
    for item in items[:3]:
        skills = [str(skill).lower() for skill in item.get("skills", []) if str(skill).strip()]
        for question in item.get("interview_prep", []) or []:
            if not str(question).strip():
                continue
            result.append(q(str(question), _keywords_from_skills(skills), "project_evidence", "C\u00e2u n\u00e0y \u0111\u01b0\u1ee3c l\u1ea5y t\u1eeb roadmap g\u1ea7n nh\u1ea5t \u0111\u1ec3 b\u1ea1n luy\u1ec7n \u0111\u00fang k\u1ebf ho\u1ea1ch h\u1ecdc t\u1eadp.", skills, "roadmap"))
    return result


def _keywords_from_skills(skills: list[str]) -> list[str]:
    keywords = _dedupe(skills + ["project", "example", "tradeoff", "debug"])
    return keywords[:6] or ["project", "example", "skill", "tradeoff"]


def _with_reason(question: Question, reason: str) -> Question:
    updated = dict(question)
    updated["reason"] = reason
    return updated


def _dedupe_questions(questions: list[Question]) -> list[Question]:
    seen = set()
    result: list[Question] = []
    for question in questions:
        text = str(question["question"])
        if text not in seen:
            result.append(question)
            seen.add(text)
    return result


def _dedupe(items: list[str]) -> list[str]:
    result: list[str] = []
    seen = set()
    for item in items:
        normalized = item.strip().lower()
        if normalized and normalized not in seen:
            result.append(normalized)
            seen.add(normalized)
    return result


def _as_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item).strip()]
