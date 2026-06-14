import builtins

from conftest import auth_headers, create_analysis, upload_resume
from app.services import resume_job_matcher


def test_create_resume_and_jd_then_run_analysis(client):
    headers = auth_headers(client)

    analysis = create_analysis(client, headers)

    assert "match_score" in analysis
    assert "scoring_breakdown" in analysis
    assert "skill_gap_summary" in analysis
    assert "prioritized_missing_skills" in analysis
    assert "improvement_plan" in analysis
    assert {
        "skill_score",
        "keyword_score",
        "semantic_score",
        "role_alignment_score",
        "evidence_score",
        "confidence",
        "length_sanity",
        "final_score",
    }.issubset(set(analysis["scoring_breakdown"].keys()))


def test_analysis_missing_resume_returns_404(client):
    headers = auth_headers(client)

    response = client.post(
        "/api/analysis/resume-job-match",
        json={"resume_id": 999, "job_description_id": 999},
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json()["code"] == "RESUME_NOT_FOUND"


def test_analysis_missing_job_description_returns_404(client):
    headers = auth_headers(client)
    resume = upload_resume(client, headers)

    response = client.post(
        "/api/analysis/resume-job-match",
        json={"resume_id": resume["id"], "job_description_id": 999},
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json()["code"] == "JOB_DESCRIPTION_NOT_FOUND"


def test_sentence_transformers_disabled_uses_rule_based_scoring(monkeypatch):
    monkeypatch.setenv("SENTENCE_TRANSFORMERS_ENABLED", "false")
    resume_job_matcher.SEMANTIC_MODEL = None
    resume_job_matcher.SEMANTIC_MODEL_LOAD_ERROR = None
    original_import = builtins.__import__

    def fail_on_sentence_transformers(name, *args, **kwargs):
        if name.startswith("sentence_transformers"):
            raise AssertionError("sentence_transformers should not be imported when disabled")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fail_on_sentence_transformers)

    result = resume_job_matcher.analyze_resume_job_match(
        "Python FastAPI PostgreSQL REST API JWT backend project with authentication and SQL database.",
        "Backend role requiring Python FastAPI PostgreSQL Docker REST API JWT authentication.",
    )

    assert result["scoring_breakdown"]["semantic_score"] == 0.0
    assert result["match_score"] > 0


def test_matching_v2_penalizes_frontend_cv_for_backend_jd(monkeypatch):
    monkeypatch.setenv("SENTENCE_TRANSFORMERS_ENABLED", "false")
    result = resume_job_matcher.analyze_resume_job_match(
        "Frontend React TypeScript project. Built UI components, forms, API integration with Next.js and Tailwind. Experience with HTML CSS JavaScript React.",
        "Backend Intern role requiring Python FastAPI PostgreSQL REST API JWT authentication Docker and SQL database.",
    )

    breakdown = result["scoring_breakdown"]
    assert breakdown["resume_role_family"] == "frontend"
    assert breakdown["jd_role_family"] == "backend"
    assert breakdown["role_alignment_score"] <= 6
    assert result["match_score"] < 45


def test_matching_v2_detects_same_role_different_stack(monkeypatch):
    monkeypatch.setenv("SENTENCE_TRANSFORMERS_ENABLED", "false")
    result = resume_job_matcher.analyze_resume_job_match(
        "Backend developer project experience. Built ASP.NET Core REST API with C# .NET SQL PostgreSQL JWT authentication and deployed backend services.",
        "Python Backend Intern requiring Python FastAPI PostgreSQL REST API JWT authentication Docker.",
    )

    breakdown = result["scoring_breakdown"]
    assert breakdown["resume_role_family"] == "backend"
    assert breakdown["jd_role_family"] == "backend"
    assert "dotnet_backend" in breakdown["resume_stack_groups"]
    assert "python_backend" in breakdown["jd_stack_groups"]
    assert "fastapi" in breakdown["critical_skills"]
    assert result["match_score"] < 80


def test_matching_v2_keeps_exact_backend_fit_high(monkeypatch):
    monkeypatch.setenv("SENTENCE_TRANSFORMERS_ENABLED", "false")
    result = resume_job_matcher.analyze_resume_job_match(
        "Backend project experience. Built Python FastAPI REST API with PostgreSQL database, JWT authentication, SQLAlchemy ORM and Docker deployment. Implemented users, auth, validation, database migrations and deployed backend platform for a production-style project.",
        "Backend Intern requiring Python FastAPI PostgreSQL REST API JWT authentication SQLAlchemy Docker and database project experience.",
    )

    breakdown = result["scoring_breakdown"]
    assert breakdown["resume_role_family"] == "backend"
    assert breakdown["jd_role_family"] == "backend"
    assert breakdown["evidence_score"] >= 10
    assert result["match_score"] >= 75


def test_matching_v2_short_cv_has_low_confidence(monkeypatch):
    monkeypatch.setenv("SENTENCE_TRANSFORMERS_ENABLED", "false")
    result = resume_job_matcher.analyze_resume_job_match(
        "Python FastAPI SQL",
        "Backend Intern requiring Python FastAPI PostgreSQL REST API JWT authentication Docker and database experience.",
    )

    assert result["scoring_breakdown"]["confidence"] == "low"
    assert result["match_score"] <= 65


