from conftest import auth_headers, create_analysis, upload_resume


def test_create_resume_and_jd_then_run_analysis(client):
    headers = auth_headers(client)

    analysis = create_analysis(client, headers)

    assert "match_score" in analysis
    assert "scoring_breakdown" in analysis
    assert "skill_gap_summary" in analysis
    assert "prioritized_missing_skills" in analysis
    assert "improvement_plan" in analysis
    assert set(analysis["scoring_breakdown"].keys()) == {
        "skill_score",
        "keyword_score",
        "semantic_score",
        "length_sanity",
        "final_score",
    }


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
