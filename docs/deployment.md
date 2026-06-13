# CareerOS AI Deployment Guide

This guide prepares the current MVP for Render backend deployment and Vercel frontend deployment. It does not add new business features.

## Deployment Targets

- Backend: Render Web Service
- Frontend: Vercel
- Database: PostgreSQL / Supabase
- Storage: currently local backend filesystem; production should move to Supabase Storage

## Backend on Render

Recommended service type: Render Web Service.

Use `backend/` as the service root directory.

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Health check path:

```text
/health
```

Python runtime:

```text
python-3.11.9
```

The repository includes `backend/runtime.txt` and `backend/render.yaml` as a baseline Render configuration. Manual setup in the Render dashboard is also fine.

### Backend Environment Variables

Set these variables in Render:

```text
PROJECT_NAME=CareerOS AI API
DATABASE_URL=postgresql://...
JWT_SECRET_KEY=<strong-random-secret>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
BACKEND_CORS_ORIGINS=https://your-vercel-app.vercel.app,http://localhost:3000
SENTENCE_TRANSFORMERS_LOCAL_FILES_ONLY=true
LOG_LEVEL=INFO
```

Do not commit `.env`. Keep secrets only in Render environment variables.

### CORS

Local development origin:

```text
http://localhost:3000
```

Production frontend origin:

```text
https://your-vercel-app.vercel.app
```

`BACKEND_CORS_ORIGINS` supports multiple comma-separated origins. Avoid `*` in production because authenticated requests use JWT and should be limited to known frontend domains.

### Sentence Transformers on Render

CareerOS AI uses rule-based matching plus optional Sentence Transformers semantic similarity.

For Render free or small instances, keep:

```text
SENTENCE_TRANSFORMERS_LOCAL_FILES_ONLY=true
```

With this setting, the backend does not try to download `all-MiniLM-L6-v2` at runtime. If the model is not cached, matching falls back to rule-based scoring and the app remains usable.

Only set `SENTENCE_TRANSFORMERS_LOCAL_FILES_ONLY=false` if the deployment environment has enough resources and network access for model download.

### Backend Storage Limitation

Current upload storage is local:

- `backend/uploads/resumes`
- `backend/uploads/job_descriptions`

Render filesystem is not durable unless persistent disk is configured. Uploaded CV/JD files may be lost across deploys/restarts on free or ephemeral storage.

Production-ready storage should move to Supabase Storage in a future phase. The database already has `storage_path` / `file_url` style fields to support that migration.

## Frontend on Vercel

Use `frontend/` as the Vercel project root.

Install/build commands can use Vercel defaults:

```bash
npm install
npm run build
```

Set this environment variable in Vercel:

```text
NEXT_PUBLIC_API_URL=https://your-render-backend-url.onrender.com
```

Do not use `http://localhost:8000` in production. The frontend API clients read the backend URL from `NEXT_PUBLIC_API_URL`.

## Deployment Checklist

Backend:

- Render service root is `backend/`.
- Build command is `pip install -r requirements.txt`.
- Start command is `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
- `/health` returns ok after deploy.
- `DATABASE_URL` points to PostgreSQL/Supabase.
- `JWT_SECRET_KEY` is strong and not committed.
- `BACKEND_CORS_ORIGINS` includes the Vercel production URL.
- `SENTENCE_TRANSFORMERS_LOCAL_FILES_ONLY=true` for stable MVP deploy unless model hosting is prepared.

Frontend:

- Vercel project root is `frontend/`.
- `NEXT_PUBLIC_API_URL` points to Render backend URL.
- `npm run build` passes locally before deploy.
- Login/register/dashboard calls work against deployed backend.

Before real beta:

- Move upload storage to Supabase Storage or configure persistent disk.
- Add database migrations before frequent schema changes.
- Review localStorage JWT risk for production security.
- Add monitoring/error tracking when traffic begins.
