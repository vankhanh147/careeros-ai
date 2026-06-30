from types import SimpleNamespace

from conftest import auth_headers, upload_resume

from app.routers import resumes


class FakeSignedUrlStorage:
    enabled = True

    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}
        self.signed_paths: list[tuple[str, int]] = []

    def upload_bytes(self, storage_path: str, content: bytes, content_type: str) -> None:
        self.objects[storage_path] = content

    def create_signed_url(self, storage_path: str, expires_in_seconds: int) -> str:
        self.signed_paths.append((storage_path, expires_in_seconds))
        return f"https://storage.example.test/signed/{storage_path}?token=short-lived"


def test_owner_can_get_resume_access_url(client, monkeypatch):
    storage = FakeSignedUrlStorage()
    monkeypatch.setattr(resumes, "get_storage_service", lambda: storage)
    headers = auth_headers(client)
    resume = upload_resume(client, headers)

    response = client.get(f"/api/resumes/{resume['id']}/access-url", headers=headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["resume_id"] == resume["id"]
    assert payload["access_url"].startswith("https://storage.example.test/signed/")
    assert payload["expires_in_seconds"] == 300
    assert payload["storage_provider"] == "supabase"
    assert payload["download_filename"] == resume["file_name"]
    assert storage.signed_paths == [(resume["storage_path"], 300)]


def test_other_user_cannot_get_resume_access_url(client, monkeypatch):
    storage = FakeSignedUrlStorage()
    monkeypatch.setattr(resumes, "get_storage_service", lambda: storage)
    owner_headers = auth_headers(client, email="owner@example.com", full_name="Owner")
    resume = upload_resume(client, owner_headers)
    other_headers = auth_headers(client, email="other@example.com", full_name="Other")

    response = client.get(f"/api/resumes/{resume['id']}/access-url", headers=other_headers)

    assert response.status_code == 404
    assert response.json()["code"] == "RESUME_NOT_FOUND"
    assert storage.signed_paths == []


def test_missing_resume_returns_404(client):
    headers = auth_headers(client)

    response = client.get("/api/resumes/999999/access-url", headers=headers)

    assert response.status_code == 404
    assert response.json()["code"] == "RESUME_NOT_FOUND"


def test_missing_storage_path_returns_friendly_error(client, monkeypatch):
    headers = auth_headers(client)
    monkeypatch.setattr(
        resumes,
        "_get_user_resume",
        lambda resume_id, user_id, db: SimpleNamespace(
            id=resume_id,
            user_id=user_id,
            file_name="resume.pdf",
            storage_path="",
        ),
    )

    response = client.get("/api/resumes/1/access-url", headers=headers)

    assert response.status_code == 409
    assert response.json()["code"] == "RESUME_STORAGE_PATH_MISSING"


def test_missing_supabase_configuration_returns_friendly_error(client):
    headers = auth_headers(client)
    resume = upload_resume(client, headers)

    response = client.get(f"/api/resumes/{resume['id']}/access-url", headers=headers)

    assert response.status_code == 503
    assert response.json()["code"] == "RESUME_ACCESS_UNAVAILABLE"


def test_access_response_does_not_expose_secret_or_persist_url(client, monkeypatch):
    storage = FakeSignedUrlStorage()
    monkeypatch.setattr(resumes, "get_storage_service", lambda: storage)
    headers = auth_headers(client)
    resume = upload_resume(client, headers)

    response = client.get(f"/api/resumes/{resume['id']}/access-url", headers=headers)
    list_response = client.get("/api/resumes/me", headers=headers)

    assert response.status_code == 200
    response_text = response.text.lower()
    assert "service_role" not in response_text
    assert "secret" not in response_text
    stored_resume = next(item for item in list_response.json() if item["id"] == resume["id"])
    assert stored_resume["file_url"] is None
