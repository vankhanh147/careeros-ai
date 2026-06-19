"""Skill graph foundation for CareerOS AI.

This module stores normalized skill metadata for future intelligence layers. It is
not integrated into production scoring in Phase 8.1.
"""

from __future__ import annotations

from typing import TypedDict


class SkillNode(TypedDict):
    """A normalized skill node and its graph metadata."""

    aliases: list[str]
    category: str
    related_skills: list[str]


SKILL_GRAPH: dict[str, SkillNode] = {
    "JWT": {
        "aliases": ["json web token", "jwt token", "access token"],
        "category": "authentication",
        "related_skills": ["Authentication", "Authorization", "OAuth2", "REST API", "API security"],
    },
    "Authentication": {
        "aliases": ["auth", "login system", "sign in", "identity"],
        "category": "security",
        "related_skills": ["JWT", "Authorization", "OAuth2", "session management", "password hashing"],
    },
    "Authorization": {
        "aliases": ["access control", "permission", "role-based access", "rbac"],
        "category": "security",
        "related_skills": ["Authentication", "JWT", "OAuth2", "RBAC", "API security"],
    },
    "OAuth2": {
        "aliases": ["oauth", "oauth 2", "social login", "identity provider"],
        "category": "authentication",
        "related_skills": ["Authentication", "Authorization", "JWT", "OpenID Connect"],
    },
    "React": {
        "aliases": ["reactjs", "react.js"],
        "category": "frontend",
        "related_skills": ["Next.js", "TypeScript", "JavaScript", "component state", "REST API integration"],
    },
    "Next.js": {
        "aliases": ["nextjs", "next js"],
        "category": "frontend",
        "related_skills": ["React", "TypeScript", "App Router", "server rendering", "Vercel"],
    },
    "TypeScript": {
        "aliases": ["ts"],
        "category": "programming_language",
        "related_skills": ["JavaScript", "React", "Next.js", "type safety"],
    },
    "JavaScript": {
        "aliases": ["js", "ecmascript"],
        "category": "programming_language",
        "related_skills": ["TypeScript", "React", "Node.js", "frontend"],
    },
    "FastAPI": {
        "aliases": ["fast api"],
        "category": "backend_framework",
        "related_skills": ["Python", "REST API", "Python Backend", "Pydantic", "SQLAlchemy"],
    },
    "REST API": {
        "aliases": ["rest", "restful api", "api endpoint", "web api"],
        "category": "backend",
        "related_skills": ["FastAPI", "ASP.NET Core", "Node.js", "Authentication", "API design"],
    },
    "Python Backend": {
        "aliases": ["python api", "backend python", "python web backend"],
        "category": "backend_stack",
        "related_skills": ["Python", "FastAPI", "Django", "Flask", "SQLAlchemy", "REST API"],
    },
    "Python": {
        "aliases": ["py"],
        "category": "programming_language",
        "related_skills": ["FastAPI", "Django", "Flask", "pandas", "machine learning"],
    },
    "ASP.NET Core": {
        "aliases": ["asp net core", "asp.net", "asp net", "aspnet core", "aspnetcore", ".net web api"],
        "category": "backend_framework",
        "related_skills": ["C#", ".NET", "REST API", "Entity Framework Core", "JWT"],
    },
    ".NET": {
        "aliases": ["dotnet", "dot net"],
        "category": "backend_stack",
        "related_skills": ["C#", "ASP.NET Core", "Entity Framework Core", "SQL Server"],
    },
    "C#": {
        "aliases": ["c sharp", "csharp"],
        "category": "programming_language",
        "related_skills": [".NET", "ASP.NET Core", "Entity Framework Core"],
    },
    "Node.js": {
        "aliases": ["nodejs", "node js"],
        "category": "backend_runtime",
        "related_skills": ["Express", "JavaScript", "TypeScript", "REST API"],
    },
    "Express": {
        "aliases": ["express.js", "expressjs"],
        "category": "backend_framework",
        "related_skills": ["Node.js", "REST API", "JWT", "MongoDB"],
    },
    "PostgreSQL": {
        "aliases": ["postgres", "postgres sql"],
        "category": "database",
        "related_skills": ["SQL", "database design", "SQLAlchemy", "Supabase"],
    },
    "SQL": {
        "aliases": ["structured query language"],
        "category": "database",
        "related_skills": ["PostgreSQL", "MySQL", "data modeling", "query optimization"],
    },
    "Supabase": {
        "aliases": ["supabase postgres", "supabase storage"],
        "category": "backend_platform",
        "related_skills": ["PostgreSQL", "Supabase Storage", "Authentication", "REST API"],
    },
    "Docker": {
        "aliases": ["container", "containerization"],
        "category": "devops",
        "related_skills": ["Kubernetes", "deployment", "CI/CD", "Linux"],
    },
    "CI/CD": {
        "aliases": ["ci cd", "continuous integration", "continuous delivery"],
        "category": "devops",
        "related_skills": ["GitHub Actions", "Docker", "deployment automation", "testing"],
    },
    "Flutter": {
        "aliases": ["flutter mobile"],
        "category": "mobile",
        "related_skills": ["Dart", "Firebase", "mobile UI", "REST API integration"],
    },
    "Firebase": {
        "aliases": ["firebase auth", "firestore"],
        "category": "backend_platform",
        "related_skills": ["Flutter", "mobile backend", "Authentication", "push notification"],
    },
    "machine learning": {
        "aliases": ["ml", "machine-learning"],
        "category": "ai_ml",
        "related_skills": ["Python", "scikit-learn", "pandas", "model evaluation", "feature engineering"],
    },
    "NLP": {
        "aliases": ["natural language processing", "text processing"],
        "category": "ai_ml",
        "related_skills": ["machine learning", "Sentence Transformers", "text classification", "embeddings"],
    },
    "Sentence Transformers": {
        "aliases": ["sentence-transformers", "sbert", "embeddings"],
        "category": "ai_ml",
        "related_skills": ["NLP", "semantic similarity", "Python", "model evaluation"],
    },
    "pandas": {
        "aliases": ["python pandas"],
        "category": "data_analysis",
        "related_skills": ["Python", "NumPy", "data cleaning", "data analysis"],
    },
    "Power BI": {
        "aliases": ["powerbi", "bi dashboard"],
        "category": "data_visualization",
        "related_skills": ["data visualization", "DAX", "business metrics", "SQL"],
    },
    "Playwright": {
        "aliases": ["playwright testing"],
        "category": "testing",
        "related_skills": ["frontend testing", "E2E testing", "QA / Testing", "TypeScript"],
    },
    "OWASP Top 10": {
        "aliases": ["owasp", "web security risks"],
        "category": "cybersecurity",
        "related_skills": ["secure coding", "Authentication", "Authorization", "API security"],
    },
}


def get_skill_node(skill: str) -> SkillNode | None:
    """Return a skill node by canonical skill name, case-insensitive."""

    normalized = skill.strip().lower()
    for canonical, node in SKILL_GRAPH.items():
        if canonical.lower() == normalized:
            return node
    return None


def normalize_skill_alias(skill_or_alias: str) -> str | None:
    """Return canonical skill name for a skill or alias."""

    normalized = skill_or_alias.strip().lower()
    for canonical, node in SKILL_GRAPH.items():
        if canonical.lower() == normalized:
            return canonical
        if normalized in {alias.lower() for alias in node["aliases"]}:
            return canonical
    return None


def related_skills(skill: str) -> list[str]:
    """Return related skills for a canonical skill or alias."""

    canonical = normalize_skill_alias(skill)
    if not canonical:
        return []
    return SKILL_GRAPH[canonical]["related_skills"]


def skills_by_category(category: str) -> dict[str, SkillNode]:
    """Return all skills in a category."""

    normalized = category.strip().lower()
    return {
        skill: node
        for skill, node in SKILL_GRAPH.items()
        if node["category"].lower() == normalized
    }
