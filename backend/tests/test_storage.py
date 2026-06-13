from conftest import auth_headers, create_job_description, fake_pdf_bytes


class FakeStorageService:
    enabled = True

    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}
        self.deleted: list[str] = []

    def upload_bytes(self, storage_path: str, content: bytes, content_type: str) -> None:
        self.objects[storage_path] = content

    def download_bytes(self, storage_path: str) -> bytes:
        return self.objects[storage_path]

    def delete_object(self, storage_path: str) -> bool:
        self.deleted.append(storage_path)
        self.objects.pop(storage_path, None)
        return True


def test_resume_upload_analysis_and_delete_use_supabase_storage(client, monkeypatch):
    fake_storage = FakeStorageService()
    from app.routers import analysis, resumes
    from app.services import storage as storage_module

    monkeypatch.setattr(resumes, "get_storage_service", lambda: fake_storage)
    monkeypatch.setattr(storage_module, "get_storage_service", lambda: fake_storage)
    monkeypatch.setattr(analysis, "readable_file_path", storage_module.readable_file_path)

    headers = auth_headers(client)
    upload_response = client.post(
        "/api/resumes/upload",
        files={"file": ("resume.pdf", fake_pdf_bytes(), "application/pdf")},
        headers=headers,
    )
    assert upload_response.status_code == 201, upload_response.text
    resume = upload_response.json()
    assert resume["storage_path"].startswith(f"users/{resume['user_id']}/resumes/")
    assert resume["storage_path"] in fake_storage.objects

    jd = create_job_description(client, headers)
    analysis_response = client.post(
        "/api/analysis/resume-job-match",
        json={"resume_id": resume["id"], "job_description_id": jd["id"]},
        headers=headers,
    )
    assert analysis_response.status_code == 201, analysis_response.text

    delete_response = client.delete(f"/api/resumes/{resume['id']}", headers=headers)
    assert delete_response.status_code == 204
    assert resume["storage_path"] in fake_storage.deleted


def test_job_description_upload_and_delete_use_supabase_storage(client, monkeypatch):
    fake_storage = FakeStorageService()
    from app.routers import job_descriptions

    monkeypatch.setattr(job_descriptions, "get_storage_service", lambda: fake_storage)

    headers = auth_headers(client)
    upload_response = client.post(
        "/api/job-descriptions/upload",
        files={"file": ("jd.txt", b"Python FastAPI PostgreSQL Docker", "text/plain")},
        data={"title": "Uploaded JD", "company": "Example Co"},
        headers=headers,
    )
    assert upload_response.status_code == 201, upload_response.text
    jd = upload_response.json()
    assert jd["storage_path"].startswith(f"users/{jd['user_id']}/job-descriptions/")
    assert jd["storage_path"] in fake_storage.objects

    delete_response = client.delete(f"/api/job-descriptions/{jd['id']}", headers=headers)
    assert delete_response.status_code == 204
    assert jd["storage_path"] in fake_storage.deleted
