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


def test_dashboard_summary_includes_roadmap_completion_progress(client):
    headers = auth_headers(client)
    create_profile(client, headers)
    analysis = create_analysis(client, headers)
    roadmap_response = client.post(
        "/api/roadmaps/generate",
        json={"analysis_id": analysis["id"], "timeline": "2 tuan"},
        headers=headers,
    )
    assert roadmap_response.status_code == 201, roadmap_response.text
    update_response = client.patch(
        "/api/roadmaps/latest/items/0/completion",
        json={"completed": True},
        headers=headers,
    )
    assert update_response.status_code == 200, update_response.text

    response = client.get("/api/dashboard/summary", headers=headers)

    assert response.status_code == 200
    dashboard = response.json()
    assert dashboard["latest_roadmap"]["completed_items"] == 1
    assert dashboard["latest_roadmap"]["total_items"] == 2
    assert dashboard["learning_loop_summary"] == "\u0110\u00e3 ho\u00e0n th\u00e0nh 1/2 m\u1ee5c roadmap"
    assert dashboard["should_rerun_analysis"] is True


def test_dashboard_suggests_rerun_when_resume_is_newer_than_analysis(client):
    headers = auth_headers(client)
    create_profile(client, headers)
    create_analysis(client, headers)
    upload_resume(client, headers, file_name="updated-resume.pdf")

    response = client.get("/api/dashboard/summary", headers=headers)

    assert response.status_code == 200
    dashboard = response.json()
    assert dashboard["has_new_resume_after_analysis"] is True
    assert dashboard["should_rerun_analysis"] is True
    assert any("CV m\u1edbi" in action for action in dashboard["recommended_next_actions"])

