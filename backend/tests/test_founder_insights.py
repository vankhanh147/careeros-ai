from app.database import get_db
from app.main import app
from app.models.user import User
from conftest import auth_headers, create_analysis, create_profile


def promote_user(client, email="user@example.com", role="founder"):
    override = app.dependency_overrides[get_db]
    db_gen = override()
    db = next(db_gen)
    try:
        user = db.query(User).filter(User.email == email).first()
        assert user is not None
        user.role = role
        db.commit()
    finally:
        db.close()


def test_founder_insights_requires_founder_role(client):
    headers = auth_headers(client)

    response = client.get("/api/founder/insights", headers=headers)

    assert response.status_code == 403
    assert response.json()["code"] == "FOUNDER_ACCESS_REQUIRED"


def test_founder_insights_empty_data_fallback(client):
    headers = auth_headers(client)
    promote_user(client)

    response = client.get("/api/founder/insights", headers=headers)

    assert response.status_code == 200, response.text
    insights = response.json()
    assert insights["funnel"]["registered_users"] == 1
    assert insights["funnel"]["profile_completed_users"] == 0
    assert insights["common_missing_skills"] == []
    assert insights["match_health"]["average_match_score"] == 0


def test_founder_insights_aggregates_usage_feedback_missing_skills_and_learning_loop(client):
    headers = auth_headers(client)
    promote_user(client)
    create_profile(client, headers)
    analysis = create_analysis(client, headers)

    roadmap_response = client.post(
        "/api/roadmaps/generate",
        json={"analysis_id": analysis["id"], "timeline": "2 tuan"},
        headers=headers,
    )
    assert roadmap_response.status_code == 201, roadmap_response.text
    complete_response = client.patch(
        "/api/roadmaps/latest/items/0/completion",
        json={"completed": True},
        headers=headers,
    )
    assert complete_response.status_code == 200, complete_response.text

    rerun_response = client.post(
        "/api/analysis/resume-job-match",
        json={"resume_id": analysis["resume_id"], "job_description_id": analysis["job_description_id"]},
        headers=headers,
    )
    assert rerun_response.status_code == 201, rerun_response.text

    feedback_response = client.post(
        "/api/feedback",
        json={"feedback_type": "analysis", "useful": True, "comment": "Useful for beta review"},
        headers=headers,
    )
    assert feedback_response.status_code == 201, feedback_response.text
    feedback_response = client.post(
        "/api/feedback",
        json={"feedback_type": "roadmap", "useful": False},
        headers=headers,
    )
    assert feedback_response.status_code == 201, feedback_response.text

    start_response = client.post(
        "/api/interviews/start",
        json={"analysis_id": analysis["id"], "target_role": "Backend Developer"},
        headers=headers,
    )
    assert start_response.status_code == 201, start_response.text
    session = start_response.json()
    answer_response = client.post(
        f"/api/interviews/{session['id']}/answer",
        json={"answer_id": session["answers"][0]["id"], "user_answer": "I use FastAPI, REST API, JWT and PostgreSQL in backend projects."},
        headers=headers,
    )
    assert answer_response.status_code == 200, answer_response.text
    finish_response = client.post(f"/api/interviews/{session['id']}/finish", headers=headers)
    assert finish_response.status_code == 200, finish_response.text

    response = client.get("/api/founder/insights", headers=headers)

    assert response.status_code == 200, response.text
    insights = response.json()
    funnel = insights["funnel"]
    assert funnel["registered_users"] == 1
    assert funnel["profile_completed_users"] == 1
    assert funnel["uploaded_cv_users"] == 1
    assert funnel["uploaded_jd_users"] == 1
    assert funnel["generated_analysis_users"] == 1
    assert funnel["generated_roadmap_users"] == 1
    assert funnel["started_interview_users"] == 1
    assert funnel["completed_interview_users"] == 1

    feedback = {item["feedback_type"]: item for item in insights["feedback"]}
    assert feedback["analysis"]["useful"] == 1
    assert feedback["analysis"]["useful_rate"] == 100
    assert feedback["roadmap"]["not_useful"] == 1
    assert insights["common_missing_skills"]
    assert insights["match_health"]["total_analyses"] == 2
    assert insights["learning_loop"]["users_completing_roadmap_items"] == 1
    assert insights["learning_loop"]["completed_roadmap_items"] == 1
    assert insights["learning_loop"]["users_rerunning_analysis_after_roadmap"] == 1
