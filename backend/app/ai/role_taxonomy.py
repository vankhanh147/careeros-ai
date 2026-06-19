"""Career role taxonomy foundation for CareerOS AI.

This module is intentionally read-only/static for Phase 8.1. It does not change
production matcher behavior. Future phases can use it as a shared source of truth
for role-family detection, roadmap generation, interview selection, and benchmark
calibration.
"""

from __future__ import annotations

from typing import TypedDict


class RoleDefinition(TypedDict):
    """A normalized role definition used by CareerOS AI intelligence layers."""

    title: str
    role_family: str
    stack_groups: list[str]
    common_skills: list[str]


ROLE_TAXONOMY: dict[str, RoleDefinition] = {
    "backend_developer": {
        "title": "Backend Developer",
        "role_family": "backend",
        "stack_groups": [
            "dotnet_backend",
            "python_backend",
            "node_backend",
            "java_backend",
            "database_backend",
        ],
        "common_skills": [
            "REST API",
            "API design",
            "authentication",
            "authorization",
            "JWT",
            "OAuth2",
            "SQL",
            "PostgreSQL",
            "MySQL",
            "MongoDB",
            "FastAPI",
            "Django",
            "Flask",
            "Node.js",
            "Express",
            "ASP.NET Core",
            ".NET",
            "C#",
            "Java",
            "Spring Boot",
            "Docker",
            "Git",
            "unit testing",
        ],
    },
    "frontend_developer": {
        "title": "Frontend Developer",
        "role_family": "frontend",
        "stack_groups": [
            "react_frontend",
            "nextjs_frontend",
            "angular_frontend",
            "vue_frontend",
            "web_ui",
        ],
        "common_skills": [
            "HTML",
            "CSS",
            "JavaScript",
            "TypeScript",
            "React",
            "Next.js",
            "Angular",
            "Vue",
            "Tailwind CSS",
            "responsive UI",
            "form state",
            "REST API integration",
            "accessibility",
            "frontend testing",
            "Git",
        ],
    },
    "fullstack_developer": {
        "title": "Fullstack Developer",
        "role_family": "fullstack",
        "stack_groups": [
            "react_frontend",
            "nextjs_frontend",
            "node_backend",
            "python_backend",
            "dotnet_backend",
            "database_backend",
        ],
        "common_skills": [
            "frontend",
            "backend",
            "React",
            "Next.js",
            "TypeScript",
            "Node.js",
            "Express",
            "FastAPI",
            "REST API",
            "authentication",
            "JWT",
            "SQL",
            "PostgreSQL",
            "database design",
            "Docker",
            "Git",
        ],
    },
    "mobile_developer": {
        "title": "Mobile Developer",
        "role_family": "mobile",
        "stack_groups": [
            "flutter_mobile",
            "react_native_mobile",
            "android_native",
            "ios_native",
            "firebase_mobile",
        ],
        "common_skills": [
            "Flutter",
            "Dart",
            "React Native",
            "Android",
            "Kotlin",
            "iOS",
            "Swift",
            "Firebase",
            "mobile UI",
            "state management",
            "REST API integration",
            "push notification",
            "app deployment",
            "Git",
        ],
    },
    "ai_machine_learning": {
        "title": "AI / Machine Learning",
        "role_family": "ai/data",
        "stack_groups": [
            "python_ml",
            "nlp",
            "computer_vision",
            "ml_ops_lite",
            "data_science",
        ],
        "common_skills": [
            "Python",
            "machine learning",
            "scikit-learn",
            "pandas",
            "NumPy",
            "PyTorch",
            "TensorFlow",
            "NLP",
            "Sentence Transformers",
            "feature engineering",
            "model evaluation",
            "train/test split",
            "precision",
            "recall",
            "F1-score",
            "Git",
        ],
    },
    "data_analyst": {
        "title": "Data Analyst",
        "role_family": "data",
        "stack_groups": [
            "analytics_sql",
            "bi_reporting",
            "python_analysis",
            "spreadsheet_analysis",
        ],
        "common_skills": [
            "SQL",
            "Excel",
            "Google Sheets",
            "Power BI",
            "Tableau",
            "Python",
            "pandas",
            "data cleaning",
            "data visualization",
            "dashboarding",
            "business metrics",
            "statistical analysis",
        ],
    },
    "data_engineer": {
        "title": "Data Engineer",
        "role_family": "data",
        "stack_groups": [
            "data_pipeline",
            "warehouse",
            "cloud_data",
            "python_data_engineering",
        ],
        "common_skills": [
            "SQL",
            "Python",
            "ETL",
            "ELT",
            "data pipeline",
            "data warehouse",
            "PostgreSQL",
            "BigQuery",
            "Spark",
            "Airflow",
            "dbt",
            "Docker",
            "cloud storage",
            "data modeling",
        ],
    },
    "devops": {
        "title": "DevOps",
        "role_family": "devops",
        "stack_groups": [
            "container_platform",
            "cloud_infra",
            "ci_cd",
            "linux_ops",
            "infrastructure_as_code",
        ],
        "common_skills": [
            "Linux",
            "Docker",
            "Kubernetes",
            "CI/CD",
            "GitHub Actions",
            "Terraform",
            "AWS",
            "Azure",
            "GCP",
            "monitoring",
            "logging",
            "deployment automation",
            "networking basics",
        ],
    },
    "qa_testing": {
        "title": "QA / Testing",
        "role_family": "qa/testing",
        "stack_groups": [
            "manual_testing",
            "automation_testing",
            "api_testing",
            "frontend_testing",
            "quality_process",
        ],
        "common_skills": [
            "test case design",
            "manual testing",
            "automation testing",
            "API testing",
            "Postman",
            "pytest",
            "Playwright",
            "Cypress",
            "bug reporting",
            "regression testing",
            "test planning",
            "quality assurance",
        ],
    },
    "cybersecurity": {
        "title": "Cybersecurity",
        "role_family": "cybersecurity",
        "stack_groups": [
            "application_security",
            "network_security",
            "security_operations",
            "identity_access",
            "cloud_security",
        ],
        "common_skills": [
            "security fundamentals",
            "OWASP Top 10",
            "authentication",
            "authorization",
            "OAuth2",
            "JWT",
            "network security",
            "Linux",
            "vulnerability assessment",
            "penetration testing",
            "SIEM",
            "incident response",
            "secure coding",
        ],
    },
}


def get_role_definition(role_key: str) -> RoleDefinition | None:
    """Return a role definition by canonical key."""

    return ROLE_TAXONOMY.get(role_key)


def list_role_keys() -> list[str]:
    """Return all canonical role keys in stable order."""

    return sorted(ROLE_TAXONOMY.keys())


def roles_by_family(role_family: str) -> dict[str, RoleDefinition]:
    """Return all roles that belong to a normalized role family."""

    normalized = role_family.strip().lower()
    return {
        key: role
        for key, role in ROLE_TAXONOMY.items()
        if role["role_family"].lower() == normalized
    }
