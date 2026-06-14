from conftest import auth_headers, create_analysis, create_profile


def test_create_feedback_success(client):
    headers = auth_headers(client)

    response = client.post(
        "/api/feedback",
        json={"feedback_type": "analysis", "useful": True, "comment": "Useful signal."},
        headers=headers,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["feedback_type"] == "analysis"
    assert body["useful"] is True
    assert body["comment"] == "Useful signal."


def test_create_feedback_requires_auth(client):
    response = client.post(
        "/api/feedback",
        json={"feedback_type": "roadmap", "useful": False, "comment": "Need clearer steps."},
    )

    assert response.status_code == 401


def test_usage_summary_tracks_core_beta_events(client):
    headers = auth_headers(client)
    create_profile(client, headers)
    analysis = create_analysis(client, headers)

    roadmap_response = client.post(
        "/api/roadmaps/generate",
        json={"analysis_id": analysis["id"], "timeline": "1 tuần"},
        headers=headers,
    )
    assert roadmap_response.status_code == 201

    interview_response = client.post(
        "/api/interviews/start",
        json={"analysis_id": analysis["id"], "target_role": "Backend Developer"},
        headers=headers,
    )
    assert interview_response.status_code == 201
    session = interview_response.json()
    first_answer = session["answers"][0]

    answer_response = client.post(
        f"/api/interviews/{session['id']}/answer",
        json={"answer_id": first_answer["id"], "user_answer": "I would use Python, FastAPI, SQL and JWT in a REST API."},
        headers=headers,
    )
    assert answer_response.status_code == 200

    finish_response = client.post(f"/api/interviews/{session['id']}/finish", headers=headers)
    assert finish_response.status_code == 200

    feedback_response = client.post(
        "/api/feedback",
        json={"feedback_type": "interview", "useful": True},
        headers=headers,
    )
    assert feedback_response.status_code == 201

    response = client.get("/api/dashboard/usage-summary", headers=headers)

    assert response.status_code == 200
    summary = response.json()
    assert summary["total_resume_uploads"] == 1
    assert summary["total_analysis"] == 1
    assert summary["total_roadmaps"] == 1
    assert summary["total_interviews"] == 1
    assert summary["total_feedback"] == 1


def test_usage_summary_requires_auth(client):
    response = client.get("/api/dashboard/usage-summary")

    assert response.status_code == 401
