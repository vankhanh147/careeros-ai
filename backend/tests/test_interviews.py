from conftest import auth_headers, create_analysis, create_profile


def test_start_answer_and_finish_interview_session(client):
    headers = auth_headers(client)
    create_profile(client, headers)
    analysis = create_analysis(client, headers)

    start_response = client.post(
        "/api/interviews/start",
        json={"analysis_id": analysis["id"], "target_role": "Backend Developer"},
        headers=headers,
    )
    assert start_response.status_code == 201, start_response.text
    session = start_response.json()
    assert session["status"] == "in_progress"
    assert len(session["answers"]) == 5

    first_answer = session["answers"][0]
    answer_response = client.post(
        f"/api/interviews/{session['id']}/answer",
        json={
            "answer_id": first_answer["id"],
            "user_answer": "I would explain Python, FastAPI, REST API, authentication, JWT and PostgreSQL clearly.",
        },
        headers=headers,
    )
    assert answer_response.status_code == 200, answer_response.text
    answered_session = answer_response.json()
    assert answered_session["answers"][0]["score"] is not None
    assert answered_session["answers"][0]["feedback"]

    finish_response = client.post(f"/api/interviews/{session['id']}/finish", headers=headers)
    assert finish_response.status_code == 200, finish_response.text
    finished = finish_response.json()
    assert finished["status"] == "finished"
    assert finished["score"] is not None
    assert finished["summary"]
