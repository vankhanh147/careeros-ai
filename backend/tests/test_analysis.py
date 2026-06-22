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
    assert "ml_evaluation" in analysis
    assert analysis["ml_evaluation"]["production_safe"] is False
    assert analysis["match_score"] == analysis["scoring_breakdown"]["final_score"]
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


def test_matching_v21_ignores_negated_skills(monkeypatch):
    monkeypatch.setenv("SENTENCE_TRANSFORMERS_ENABLED", "false")
    result = resume_job_matcher.analyze_resume_job_match(
        "Marketing resume with campaign planning. No backend, no API implementation, no C#, no .NET and no authentication experience.",
        "Backend role requiring C# .NET ASP.NET Core REST API JWT authentication PostgreSQL SQL Docker.",
    )

    breakdown = result["scoring_breakdown"]
    assert breakdown["resume_role_family"] == "general software"
    assert breakdown["confidence"] == "low"
    assert "c#" not in result["matched_skills"]
    assert ".net" not in result["matched_skills"]
    assert result["match_score"] < 25


def test_matching_v21_detects_mobile_cross_domain(monkeypatch):
    monkeypatch.setenv("SENTENCE_TRANSFORMERS_ENABLED", "false")
    result = resume_job_matcher.analyze_resume_job_match(
        "Mobile developer resume. Projects: built Flutter mobile app with Firebase authentication and REST API integration.",
        "AI intern role requiring Python machine learning NLP pandas numpy scikit-learn and model evaluation.",
    )

    breakdown = result["scoring_breakdown"]
    assert breakdown["resume_role_family"] == "mobile"
    assert breakdown["jd_role_family"] == "ai/data"
    assert result["match_score"] < 60


def test_resume_feedback_u01_exact_fit_does_not_spam_critical_gaps(monkeypatch):
    monkeypatch.setenv("SENTENCE_TRANSFORMERS_ENABLED", "false")
    result = resume_job_matcher.analyze_resume_job_match(
        "Backend intern resume. Projects: built a task management backend API using C#, .NET, ASP.NET Core and PostgreSQL. Implemented REST API CRUD endpoints, JWT authentication, validation, SQL queries, Git/GitHub workflow and Docker deployment basics.",
        "Backend JD requiring C# .NET ASP.NET Core REST API JWT authentication PostgreSQL SQL Docker and testing.",
    )

    feedback = result["resume_feedback"]
    assert result["match_score"] >= 75
    assert len(feedback["critical_gaps"]) <= 2
    assert feedback["suggested_bullet_rewrites"]


def test_resume_feedback_u02_same_role_different_stack_has_stack_advice(monkeypatch):
    monkeypatch.setenv("SENTENCE_TRANSFORMERS_ENABLED", "false")
    result = resume_job_matcher.analyze_resume_job_match(
        "Backend developer resume. Projects: built e-commerce REST API using Node.js, Express, JavaScript and MongoDB. Implemented JWT authentication, database models, Git/GitHub and Docker. No C#, .NET or ASP.NET Core project.",
        "Backend JD requiring C# .NET ASP.NET Core REST API JWT authentication PostgreSQL SQL Docker and testing.",
    )

    feedback = result["resume_feedback"]
    combined = " ".join(item["message"] + " " + (item.get("suggested_edit") or "") for item in feedback["critical_gaps"] + feedback["recommended_next_edits"])
    assert ".NET" in combined or ".net" in combined or "c#" in combined.lower()
    assert "If you actually" in combined or "If you have" in combined


def test_resume_feedback_u04_role_mismatch_has_frontend_to_backend_advice(monkeypatch):
    monkeypatch.setenv("SENTENCE_TRANSFORMERS_ENABLED", "false")
    result = resume_job_matcher.analyze_resume_job_match(
        "Frontend developer resume. Projects: built React and Next.js UI with TypeScript, JavaScript, HTML, CSS and Tailwind. Integrated REST API from backend services. No backend project with C#, .NET, ASP.NET Core or database schema.",
        "Backend JD requiring C# .NET ASP.NET Core REST API JWT authentication PostgreSQL SQL Docker and testing.",
    )

    feedback = result["resume_feedback"]
    messages = " ".join(item["message"] for item in feedback["recommended_next_edits"])
    assert "frontend" in messages.lower()
    assert "backend" in messages.lower()
    assert result["scoring_breakdown"]["resume_role_family"] == "frontend"


def test_resume_feedback_u10_does_not_hallucinate_backend_skills(monkeypatch):
    monkeypatch.setenv("SENTENCE_TRANSFORMERS_ENABLED", "false")
    result = resume_job_matcher.analyze_resume_job_match(
        "Marketing and business resume. Experience: campaign planning, user research and content strategy. No software engineering project, no backend, no API implementation, no C#, no .NET and no authentication experience.",
        "Backend JD requiring C# .NET ASP.NET Core REST API JWT authentication PostgreSQL SQL Docker and testing.",
    )

    feedback = result["resume_feedback"]
    all_suggested = " ".join((item.get("suggested_edit") or "") for group in feedback.values() for item in group)
    assert result["match_score"] < 35
    assert result["scoring_breakdown"]["confidence"] == "low"
    assert "Developed ASP.NET Core backend APIs" not in all_suggested
    assert "If you actually" in all_suggested or "If you have" in all_suggested

