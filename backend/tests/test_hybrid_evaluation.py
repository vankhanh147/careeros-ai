from conftest import auth_headers, create_analysis
from app.ai.hybrid_evaluation import build_hybrid_evaluation
from app.services import resume_job_matcher


RESUME_TEXT = "Backend project experience. Built Python FastAPI REST API with PostgreSQL database, JWT authentication and Docker deployment."
JD_TEXT = "Backend Intern requiring Python FastAPI PostgreSQL REST API JWT authentication Docker and database project experience."


def test_hybrid_evaluation_appears_in_analysis_response(client):
    headers = auth_headers(client)

    analysis = create_analysis(client, headers)

    assert "hybrid_evaluation" in analysis
    hybrid = analysis["hybrid_evaluation"]
    assert hybrid["rule_based_score"] == analysis["scoring_breakdown"]["final_score"]
    assert hybrid["hybrid_score_candidate"] == analysis["match_score"]
    assert hybrid["production_safe"] is True


def test_hybrid_semantic_disabled_fallback_is_safe(monkeypatch):
    monkeypatch.setenv("SENTENCE_TRANSFORMERS_ENABLED", "false")

    result = resume_job_matcher.analyze_resume_job_match(RESUME_TEXT, JD_TEXT)
    hybrid = result["hybrid_evaluation"]

    assert hybrid["enabled"] is False
    assert hybrid["semantic_component"] is None
    assert hybrid["hybrid_score_candidate"] == result["match_score"]
    assert any("mirror" in note for note in hybrid["explanation_notes"])


def test_hybrid_metadata_does_not_change_final_score(monkeypatch):
    monkeypatch.setenv("SENTENCE_TRANSFORMERS_ENABLED", "false")

    result = resume_job_matcher.analyze_resume_job_match(RESUME_TEXT, JD_TEXT)

    assert result["match_score"] == result["scoring_breakdown"]["final_score"]
    assert result["hybrid_evaluation"]["rule_based_score"] == result["match_score"]


def test_hybrid_taxonomy_component_handles_empty_metadata():
    hybrid = build_hybrid_evaluation(
        rule_based_score=50.0,
        semantic_insights={"enabled": False, "reason": "semantic model disabled"},
        taxonomy_insights={},
        scoring_breakdown={"confidence": "medium"},
    )

    assert hybrid["production_safe"] is True
    assert hybrid["hybrid_score_candidate"] == 50.0
    assert hybrid["taxonomy_component"] >= 0