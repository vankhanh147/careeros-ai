import os
from io import BytesIO
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from pypdf import PdfWriter
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["JWT_SECRET_KEY"] = "test-secret-key"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "60"
os.environ["BACKEND_CORS_ORIGINS"] = "http://localhost:3000"
os.environ["SENTENCE_TRANSFORMERS_LOCAL_FILES_ONLY"] = "true"

from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.routers import job_descriptions, resumes  # noqa: E402


TEST_PASSWORD = "password123"


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    engine = create_engine(
        f"sqlite:///{tmp_path / 'test.db'}",
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    monkeypatch.setattr(resumes, "UPLOAD_ROOT", tmp_path / "uploads" / "resumes")
    monkeypatch.setattr(job_descriptions, "JD_UPLOAD_ROOT", tmp_path / "uploads" / "job_descriptions")

    def override_get_db() -> Any:
        db: Session = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def fake_pdf_bytes() -> bytes:
    buffer = BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    writer.write(buffer)
    return buffer.getvalue()


def register_user(
    client: TestClient,
    *,
    email: str = "user@example.com",
    full_name: str = "CareerOS User",
    password: str = TEST_PASSWORD,
) -> dict[str, Any]:
    response = client.post(
        "/api/auth/register",
        json={"email": email, "full_name": full_name, "password": password},
    )
    assert response.status_code == 201, response.text
    return response.json()


def login_user(
    client: TestClient,
    *,
    email: str = "user@example.com",
    password: str = TEST_PASSWORD,
) -> str:
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return str(response.json()["access_token"])


def auth_headers(
    client: TestClient,
    *,
    email: str = "user@example.com",
    full_name: str = "CareerOS User",
    password: str = TEST_PASSWORD,
) -> dict[str, str]:
    register_user(client, email=email, full_name=full_name, password=password)
    token = login_user(client, email=email, password=password)
    return {"Authorization": f"Bearer {token}"}


def create_profile(client: TestClient, headers: dict[str, str], timeline: str = "6 tuần") -> dict[str, Any]:
    payload = {
        "target_role": "Backend Developer",
        "current_level": "Junior",
        "skills": "Python, SQL, Git",
        "experience_summary": "Built REST API projects.",
        "projects_summary": "CareerOS AI backend modules.",
        "career_goal": "Become a backend engineer.",
        "timeline": timeline,
    }
    response = client.put("/api/career-profile/me", json=payload, headers=headers)
    assert response.status_code == 200, response.text
    return response.json()


def upload_resume(client: TestClient, headers: dict[str, str], file_name: str = "resume.pdf") -> dict[str, Any]:
    response = client.post(
        "/api/resumes/upload",
        files={"file": (file_name, fake_pdf_bytes(), "application/pdf")},
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def create_job_description(
    client: TestClient,
    headers: dict[str, str],
    *,
    title: str = "Backend Intern",
    content: str = "We need Python, FastAPI, PostgreSQL, Docker, JWT, REST API and Git.",
) -> dict[str, Any]:
    response = client.post(
        "/api/job-descriptions",
        json={
            "title": title,
            "company": "Example Co",
            "content": content,
            "source_url": "https://example.com/jobs/backend-intern",
        },
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def create_analysis(client: TestClient, headers: dict[str, str]) -> dict[str, Any]:
    resume = upload_resume(client, headers)
    jd = create_job_description(client, headers)
    response = client.post(
        "/api/analysis/resume-job-match",
        json={"resume_id": resume["id"], "job_description_id": jd["id"]},
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()
