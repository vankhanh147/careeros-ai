from conftest import auth_headers, create_profile


def test_put_career_profile_creates_and_updates_profile(client):
    headers = auth_headers(client)

    profile = create_profile(client, headers, timeline="1 tháng")
    assert profile["target_role"] == "Backend Developer"
    assert profile["timeline"] == "1 tháng"

    response = client.put(
        "/api/career-profile/me",
        json={**profile, "target_role": "Fullstack Developer", "timeline": "2 tháng"},
        headers=headers,
    )

    assert response.status_code == 200
    updated = response.json()
    assert updated["id"] == profile["id"]
    assert updated["target_role"] == "Fullstack Developer"
    assert updated["timeline"] == "2 tháng"


def test_get_career_profile_returns_user_profile(client):
    headers = auth_headers(client)
    created = create_profile(client, headers)

    response = client.get("/api/career-profile/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]
