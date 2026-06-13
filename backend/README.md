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

## Auth endpoints

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`

The app creates the initial `users` table at startup through SQLAlchemy metadata. This keeps the MVP simple; migrations can be added later when schema changes become more frequent.

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

Use the returned `access_token`:

```bash
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <access_token>"
```

Swagger UI: `http://localhost:8000/docs`
