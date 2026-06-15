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

from app.services.interview_evaluator import evaluate_interview_answer
from app.services.interview_generator import generate_interview_questions


def _question_texts(questions):
    return " ".join(str(item["question"]).lower() for item in questions)


def test_interview_v2_backend_dotnet_question_bank_selects_dotnet_jwt_api():
    questions = generate_interview_questions(
        "Backend .NET Intern",
        missing_skills=["jwt", "asp.net core"],
        analysis_context={"critical_skills": ["jwt", "asp.net core", "c#"], "stack_groups": ["dotnet_backend"]},
    )
    combined = _question_texts(questions)

    assert len(questions) == 5
    assert "jwt" in combined
    assert "asp.net" in combined or ".net" in combined
    assert any("jwt" in item.get("related_skills", []) for item in questions)
    assert all(item.get("reason") for item in questions)


def test_interview_v2_frontend_react_question_bank_selects_react_ui_api():
    questions = generate_interview_questions(
        "React Frontend Developer",
        missing_skills=["react", "rest api"],
        analysis_context={"critical_skills": ["react", "typescript"], "stack_groups": ["react_frontend"]},
    )
    combined = _question_texts(questions)

    assert len(questions) == 5
    assert "react" in combined
    assert "api" in combined or "state" in combined
    assert any(item.get("category") in {"concept", "project_evidence", "debugging", "tradeoff"} for item in questions)


def test_interview_v2_missing_skill_is_prioritized():
    questions = generate_interview_questions("Backend Developer", missing_skills=["docker", "postgresql"])

    assert "docker" in str(questions[0]["question"]).lower()
    assert "docker" in questions[0].get("related_skills", [])


def test_interview_v2_fallback_without_analysis_still_starts(client):
    headers = auth_headers(client)
    create_profile(client, headers)

    response = client.post("/api/interviews/start", json={}, headers=headers)

    assert response.status_code == 201, response.text
    session = response.json()
    assert len(session["answers"]) == 5
    assert session["answers"][0]["question_reason"]
    assert session["answers"][0]["question_category"]


def test_interview_v2_feedback_classifies_short_generic_answer():
    result = evaluate_interview_answer(
        "JWT hoat dong nhu the nao?",
        ["jwt", "token", "signature", "authorization"],
        "Em biet cai nay va em lam duoc.",
    )

    assert result["score"] < 60
    assert result["feedback_category"] in {"tr\u1ea3 l\u1eddi qu\u00e1 ng\u1eafn", "thi\u1ebfu concept", "tr\u1ea3 l\u1eddi qu\u00e1 chung"}
    assert "Ph\u00e2n lo\u1ea1i feedback" in result["feedback"]


def test_interview_v2_generated_content_avoids_long_english_copy():
    questions = generate_interview_questions("Backend .NET Intern", missing_skills=["jwt"])
    combined = str(questions)

    forbidden = ["How would you", "What did you", "High-priority", "Practice task", "Expected output"]
    assert not any(phrase in combined for phrase in forbidden)
