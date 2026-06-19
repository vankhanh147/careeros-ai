from app.ai.taxonomy_insights import build_taxonomy_insight, normalize_skill_list
from app.services import resume_job_matcher
from app.services.interview_generator import generate_interview_questions
from app.services.roadmap_generator import build_roadmap_from_analysis


def test_skill_alias_normalization_uses_skill_graph():
    normalized = normalize_skill_list(["aspnetcore", "asp.net core", "js", "javascript", "ts", "typescript"])

    assert "ASP.NET Core" in normalized
    assert "JavaScript" in normalized
    assert "TypeScript" in normalized
    assert normalized.count("ASP.NET Core") == 1
    assert normalized.count("JavaScript") == 1
    assert normalized.count("TypeScript") == 1


def test_taxonomy_insight_detects_frontend_stack_and_related_skills():
    insight = build_taxonomy_insight(["React", "Next.js", "TypeScript"])

    assert insight["role_family"] == "frontend"
    assert "react_frontend" in insight["stack_groups"]
    assert insight["normalized_skills"] == ["React", "Next.js", "TypeScript"]
    assert "REST API integration" in insight["related_skill_suggestions"]


def test_analysis_response_contains_taxonomy_insights_without_score_change(monkeypatch):
    monkeypatch.setenv("SENTENCE_TRANSFORMERS_ENABLED", "false")
    resume_text = "Frontend React Next.js TypeScript project with API integration and UI state."
    jd_text = "Frontend role requiring React Next.js TypeScript REST API integration."

    result = resume_job_matcher.analyze_resume_job_match(resume_text, jd_text)
    score_without_metadata = result["scoring_breakdown"]["final_score"]

    assert result["match_score"] == score_without_metadata
    assert "taxonomy_insights" in result
    assert result["taxonomy_insights"]["role_family"] == "frontend"
    assert "React" in result["taxonomy_insights"]["normalized_skills"]
    assert "react_frontend" in result["taxonomy_insights"]["stack_groups"]


def test_roadmap_reads_taxonomy_for_related_skills_without_schema_change():
    roadmap = build_roadmap_from_analysis(
        target_role="Frontend Developer",
        current_level="intern",
        timeline="1 tuan",
        prioritized_missing_skills={
            "high_priority": ["js", "ts"],
            "medium_priority": [],
            "low_priority": [],
        },
        improvement_plan=[],
        critical_skills=["javascript", "typescript"],
    )

    first_item = roadmap["items"][0]
    assert first_item["skills"] == ["JavaScript", "TypeScript"]
    assert any("K\u1ef9 n\u0103ng li\u00ean quan" in action for action in first_item["actions"])
    assert "completed" not in first_item


def test_interview_uses_taxonomy_aliases_for_question_selection():
    questions = generate_interview_questions(
        "Backend Intern",
        missing_skills=["aspnetcore"],
        analysis_context={"critical_skills": ["aspnetcore"], "stack_groups": []},
    )
    combined = " ".join(str(question["question"]).lower() for question in questions)

    assert "asp.net core" in combined or "middleware" in combined
