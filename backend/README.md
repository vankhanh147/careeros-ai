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

Semantic matching uses `SENTENCE_TRANSFORMERS_LOCAL_FILES_ONLY="true"` by default so local development does not hang when Hugging Face is blocked. Set it to `"false"` in an environment with internet access if you want the backend to download `all-MiniLM-L6-v2` automatically on first use.


## Error handling and logging

Backend error responses now keep `detail` as a human-readable string and add a stable `code` field:

```json
{
  "detail": "Invalid email or password",
  "code": "INVALID_CREDENTIALS"
}
```

This keeps the frontend compatible with the existing `detail` string while making errors easier to debug.

Logging uses Python standard logging. Default level is `INFO`; override with:

```text
LOG_LEVEL="DEBUG"
```

Do not log passwords, JWT tokens, database URLs, full CV/JD file content, or secrets. Current logs cover app startup/shutdown, auth success/failure, upload validation failures, analysis failures, roadmap generation failures, and interview failures.

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
- `POST /api/job-descriptions/upload`
- `GET /api/job-descriptions/me`

Uploaded PDFs are stored locally in `backend/uploads/resumes` for now. The database stores `storage_path` and nullable `file_url`, so the storage layer can move to Supabase Storage later without changing the core API shape.

## Analysis endpoints

- `POST /api/analysis/resume-job-match`
- `GET /api/analysis/history`

Resume ↔ Job Matching extracts PDF text with `pypdf`, keeps rule-based technology skill matching, and adds optional semantic similarity through `sentence-transformers` using the lightweight `all-MiniLM-L6-v2` model. If the model/library cannot load, the matcher automatically falls back to rule-based scoring. The response includes `resume_text_preview`, `jd_text_preview`, detected skills and `scoring_breakdown` with `skill_score`, `keyword_score`, `semantic_score`, `length_sanity` and `final_score`. It does not use an LLM API in this phase.

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

Upload job description file PDF/TXT:

```bash
curl -X POST http://localhost:8000/api/job-descriptions/upload \
  -H "Authorization: Bearer <access_token>" \
  -F "file=@/path/to/job-description.pdf" \
  -F "title=Backend Intern" \
  -F "company=Example Co"
```

Run resume-job analysis:

```bash
curl -X POST http://localhost:8000/api/analysis/resume-job-match \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"resume_id":1,"job_description_id":1}'
```

List analysis history:

```bash
curl http://localhost:8000/api/analysis/history \
  -H "Authorization: Bearer <access_token>"
```

Swagger UI: `http://localhost:8000/docs`
