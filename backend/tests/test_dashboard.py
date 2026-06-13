from conftest import auth_headers, create_analysis, create_job_description, create_profile, upload_resume


def test_new_user_dashboard_summary_returns_safe_response(client):
    headers = auth_headers(client)

    response = client.get("/api/dashboard/summary", headers=headers)

    assert response.status_code == 200
    dashboard = response.json()
    assert dashboard["has_career_profile"] is False
    assert dashboard["resume_count"] == 0
    assert dashboard["job_description_count"] == 0
    assert dashboard["latest_analysis"] is None
    assert dashboard["latest_roadmap"] is None
    assert dashboard["latest_interview"] is None
    assert dashboard["recommended_next_actions"]


def test_dashboard_summary_with_data_returns_counts_and_latest_fields(client):
    headers = auth_headers(client)
    create_profile(client, headers)
    upload_resume(client, headers)
    create_job_description(client, headers)
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

    response = client.get("/api/dashboard/summary", headers=headers)

    assert response.status_code == 200
    dashboard = response.json()
    assert dashboard["has_career_profile"] is True
    assert dashboard["resume_count"] == 2
    assert dashboard["job_description_count"] == 2
    assert dashboard["latest_analysis"]["match_score"] == analysis["match_score"]
    assert dashboard["latest_roadmap"]["title"]
    assert dashboard["latest_interview"]["status"] == "in_progress"
