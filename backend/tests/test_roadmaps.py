import pytest

from conftest import auth_headers, create_analysis, create_profile


def test_generate_roadmap_from_career_profile(client):
    headers = auth_headers(client)
    create_profile(client, headers, timeline="1 tháng")

    response = client.post("/api/roadmaps/generate", json={}, headers=headers)

    assert response.status_code == 201
    roadmap = response.json()
    assert roadmap["target_role"] == "Backend Developer"
    assert len(roadmap["items"]) == 4
    assert roadmap["items"][0]["practice_task"]
    assert roadmap["items"][0]["cv_evidence_output"]
    assert roadmap["items"][0]["interview_prep"]


def test_generate_roadmap_from_analysis(client):
    headers = auth_headers(client)
    create_profile(client, headers)
    analysis = create_analysis(client, headers)

    response = client.post(
        "/api/roadmaps/generate",
        json={"analysis_id": analysis["id"], "timeline": "2 tuần"},
        headers=headers,
    )

    assert response.status_code == 201
    roadmap = response.json()
    assert roadmap["analysis_id"] == analysis["id"]
    assert len(roadmap["items"]) == 2
    assert all(item["practice_task"] for item in roadmap["items"])
    assert all(item["cv_evidence_output"] for item in roadmap["items"])
    assert all(item["interview_prep"] for item in roadmap["items"])
    assert roadmap["items"][0]["priority"] in {"high", "medium", "low"}


@pytest.mark.parametrize(
    ("timeline", "expected_count"),
    [
        ("1 tuần", 1),
        ("2 tuần", 2),
        ("1 tháng", 4),
        (None, 6),
    ],
)
def test_timeline_parser_generates_expected_item_count(client, timeline, expected_count):
    headers = auth_headers(client)
    create_profile(client, headers, timeline="")
    payload = {} if timeline is None else {"timeline": timeline}

    response = client.post("/api/roadmaps/generate", json=payload, headers=headers)

    assert response.status_code == 201, response.text
    roadmap = response.json()
    assert len(roadmap["items"]) == expected_count
    assert f"Roadmap {expected_count}" in roadmap["title"]


def test_roadmap_v2_prioritizes_missing_critical_skills(client):
    headers = auth_headers(client)
    create_profile(client, headers)
    analysis = create_analysis(client, headers)

    response = client.post(
        "/api/roadmaps/generate",
        json={"analysis_id": analysis["id"], "timeline": "4 tu?n"},
        headers=headers,
    )

    assert response.status_code == 201, response.text
    roadmap = response.json()
    priorities = [item["priority"] for item in roadmap["items"]]
    assert "high" in priorities
    first_high = next(item for item in roadmap["items"] if item["priority"] == "high")
    assert first_high["practice_task"]
    assert first_high["cv_evidence_output"]
    assert first_high["interview_prep"]


def test_roadmap_v2_profile_fallback_is_lower_personalization(client):
    headers = auth_headers(client)
    create_profile(client, headers, timeline="2 tu?n")

    response = client.post("/api/roadmaps/generate", json={}, headers=headers)

    assert response.status_code == 201, response.text
    roadmap = response.json()
    assert "profile only" in roadmap["summary"].lower()
    assert len(roadmap["items"]) == 2
    assert all(item["practice_task"] for item in roadmap["items"])
    assert all(item["cv_evidence_output"] for item in roadmap["items"])
    assert all(item["interview_prep"] for item in roadmap["items"])

