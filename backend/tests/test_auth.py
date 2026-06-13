from conftest import TEST_PASSWORD, auth_headers, login_user, register_user


def test_register_user_success(client):
    user = register_user(client)

    assert user["email"] == "user@example.com"
    assert user["full_name"] == "CareerOS User"
    assert user["role"] == "user"
    assert user["is_active"] is True


def test_duplicate_email_returns_409(client):
    register_user(client)

    response = client.post(
        "/api/auth/register",
        json={"email": "user@example.com", "full_name": "Second User", "password": TEST_PASSWORD},
    )

    assert response.status_code == 409
    assert response.json()["code"] == "EMAIL_ALREADY_REGISTERED"


def test_login_success_returns_access_token(client):
    register_user(client)

    token = login_user(client)

    assert token


def test_login_wrong_password_returns_401(client):
    register_user(client)

    response = client.post("/api/auth/login", json={"email": "user@example.com", "password": "wrongpass123"})

    assert response.status_code == 401
    assert response.json()["code"] == "INVALID_CREDENTIALS"


def test_protected_endpoint_without_token_returns_401(client):
    response = client.get("/api/auth/me")

    assert response.status_code == 401


def test_me_with_token_returns_current_user(client):
    headers = auth_headers(client)

    response = client.get("/api/auth/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["email"] == "user@example.com"
