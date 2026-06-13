from conftest import auth_headers, create_job_description, fake_pdf_bytes, upload_resume


def test_upload_cv_pdf_success(client):
    headers = auth_headers(client)

    resume = upload_resume(client, headers, file_name="backend_resume.pdf")

    assert resume["file_name"] == "backend_resume.pdf"
    assert resume["storage_path"].endswith(".pdf")


def test_upload_wrong_cv_file_type_returns_400(client):
    headers = auth_headers(client)

    response = client.post(
        "/api/resumes/upload",
        files={"file": ("resume.txt", b"not a pdf", "text/plain")},
        headers=headers,
    )

    assert response.status_code == 400
    assert response.json()["code"] == "INVALID_FILE_TYPE"


def test_create_update_delete_job_description_success(client):
    headers = auth_headers(client)
    jd = create_job_description(client, headers)

    update_response = client.put(
        f"/api/job-descriptions/{jd['id']}",
        json={
            "title": "Backend Engineer Intern",
            "company": "Updated Co",
            "content": "Python FastAPI PostgreSQL Docker authentication",
            "source_url": "https://example.com/updated",
        },
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Backend Engineer Intern"

    delete_response = client.delete(f"/api/job-descriptions/{jd['id']}", headers=headers)
    assert delete_response.status_code == 204

    list_response = client.get("/api/job-descriptions/me", headers=headers)
    assert list_response.status_code == 200
    assert list_response.json() == []


def test_user_cannot_delete_another_users_job_description(client):
    first_headers = auth_headers(client, email="first@example.com", full_name="First User")
    jd = create_job_description(client, first_headers)
    second_headers = auth_headers(client, email="second@example.com", full_name="Second User")

    response = client.delete(f"/api/job-descriptions/{jd['id']}", headers=second_headers)

    assert response.status_code == 404
    assert response.json()["code"] == "JOB_DESCRIPTION_NOT_FOUND"


def test_delete_resume_success(client):
    headers = auth_headers(client)
    resume = upload_resume(client, headers)

    response = client.delete(f"/api/resumes/{resume['id']}", headers=headers)

    assert response.status_code == 204
    list_response = client.get("/api/resumes/me", headers=headers)
    assert list_response.status_code == 200
    assert list_response.json() == []


def test_upload_job_description_txt_success(client):
    headers = auth_headers(client)

    response = client.post(
        "/api/job-descriptions/upload",
        files={"file": ("jd.txt", b"Python FastAPI PostgreSQL Docker", "text/plain")},
        data={"title": "Uploaded JD", "company": "Example Co"},
        headers=headers,
    )

    assert response.status_code == 201
    assert response.json()["content"] == "Python FastAPI PostgreSQL Docker"


def test_upload_job_description_wrong_file_type_returns_400(client):
    headers = auth_headers(client)

    response = client.post(
        "/api/job-descriptions/upload",
        files={"file": ("jd.docx", b"docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
        headers=headers,
    )

    assert response.status_code == 400
    assert response.json()["code"] == "INVALID_FILE_TYPE"
