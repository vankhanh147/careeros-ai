import builtins

from conftest import auth_headers, create_analysis
from app.ai import semantic_matcher
from app.services import resume_job_matcher


RESUME_TEXT = "Backend project experience. Built Python FastAPI REST API with PostgreSQL database, JWT authentication, SQLAlchemy ORM and Docker deployment. Implemented users, auth, validation, database migrations and deployed backend platform for a production-style project."
JD_TEXT = "Backend Intern requiring Python FastAPI PostgreSQL REST API JWT authentication SQLAlchemy Docker and database project experience."


def test_semantic_disabled_fallback_does_not_import_sentence_transformers(monkeypatch):
    monkeypatch.setenv("SENTENCE_TRANSFORMERS_ENABLED", "false")
    semantic_matcher.reset_semantic_model_cache()
    original_import = builtins.__import__

    def fail_on_sentence_transformers(name, *args, **kwargs):
        if name.startswith("sentence_transformers"):
            raise AssertionError("sentence_transformers should not be imported when semantic is disabled")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fail_on_sentence_transformers)

    insight = semantic_matcher.build_semantic_insights(RESUME_TEXT, JD_TEXT)

    assert insight["enabled"] is False
    assert insight["reason"] == "semantic model disabled"
    assert insight["resume_jd_similarity"] is None


def test_semantic_service_load_failure_falls_back_safely(monkeypatch):
    monkeypatch.setenv("SENTENCE_TRANSFORMERS_ENABLED", "true")
    monkeypatch.setenv("SENTENCE_TRANSFORMERS_MODEL_NAME", "test-model")
    semantic_matcher.reset_semantic_model_cache()
    original_import = builtins.__import__

    def fail_on_sentence_transformers(name, *args, **kwargs):
        if name.startswith("sentence_transformers"):
            raise ImportError("test model unavailable")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fail_on_sentence_transformers)

    insight = semantic_matcher.build_semantic_insights(RESUME_TEXT, JD_TEXT)

    assert insight["enabled"] is False
    assert insight["model_name"] == "test-model"
    assert insight["resume_jd_similarity"] is None
    assert "test model unavailable" in str(insight["reason"])


def test_analysis_response_contains_semantic_insights(client):
    headers = auth_headers(client)

    analysis = create_analysis(client, headers)

    assert "semantic_insights" in analysis
    assert analysis["semantic_insights"]["enabled"] is False
    assert analysis["semantic_insights"]["resume_jd_similarity"] is None


def test_parallel_semantic_metadata_does_not_change_final_score(monkeypatch):
    monkeypatch.setenv("SENTENCE_TRANSFORMERS_ENABLED", "false")
    semantic_matcher.reset_semantic_model_cache()

    baseline = resume_job_matcher.analyze_resume_job_match(RESUME_TEXT, JD_TEXT)

    def fake_semantic_insights(_resume_text, _job_description_text):
        return {
            "enabled": True,
            "model_name": "fake-eval-model",
            "resume_jd_similarity": 0.99,
            "confidence": "high",
            "notes": ["metadata only"],
            "reason": None,
        }

    monkeypatch.setattr(resume_job_matcher, "build_semantic_insights", fake_semantic_insights)
    with_metadata = resume_job_matcher.analyze_resume_job_match(RESUME_TEXT, JD_TEXT)

    assert with_metadata["match_score"] == baseline["match_score"]
    assert with_metadata["scoring_breakdown"]["final_score"] == baseline["scoring_breakdown"]["final_score"]
    assert with_metadata["semantic_insights"]["resume_jd_similarity"] == 0.99