# CareerOS AI Backend

FastAPI backend for CareerOS AI.

## Local development

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env
```

Update `DATABASE_URL` in `.env` with your PostgreSQL or Supabase connection string.

Example local PostgreSQL URL:

```text
DATABASE_URL="postgresql://postgres:password@localhost:5432/careeros_ai"
```

Example Supabase URL format:

```text
DATABASE_URL="postgresql://postgres:<password>@<host>:5432/postgres"
```

Set a strong `JWT_SECRET_KEY` before using the backend beyond local development.

## Run backend

```powershell
uvicorn app.main:app --reload
```

Backend URL: `http://localhost:8000`

Health check: `GET http://localhost:8000/health`

The app creates initial tables at startup through SQLAlchemy metadata. This keeps the MVP simple; migrations can be added later when schema changes become more frequent.

## Auth endpoints

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`

## Career profile endpoints

- `GET /api/career-profile/me`
- `PUT /api/career-profile/me`

## Resume and job description endpoints

- `POST /api/resumes/upload`
- `GET /api/resumes/me`
- `POST /api/job-descriptions`
- `GET /api/job-descriptions/me`

Uploaded PDFs are stored locally in `backend/uploads/resumes` for now. The database stores `storage_path` and nullable `file_url`, so the storage layer can move to Supabase Storage later without changing the core API shape.

## Manual test with curl

Register:

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","full_name":"CareerOS User","password":"password123"}'
```

Login:

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'
```

Use the returned `access_token` for protected endpoints.

Upload resume PDF:

```bash
curl -X POST http://localhost:8000/api/resumes/upload \
  -H "Authorization: Bearer <access_token>" \
  -F "file=@/path/to/resume.pdf"
```

List uploaded resumes:

```bash
curl http://localhost:8000/api/resumes/me \
  -H "Authorization: Bearer <access_token>"
```

Create job description:

```bash
curl -X POST http://localhost:8000/api/job-descriptions \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"title":"Backend Intern","company":"Example Co","content":"We need Python, FastAPI and PostgreSQL.","source_url":"https://example.com/jobs/backend-intern"}'
```

List job descriptions:

```bash
curl http://localhost:8000/api/job-descriptions/me \
  -H "Authorization: Bearer <access_token>"
```

Swagger UI: `http://localhost:8000/docs`
