# CareerOS AI Deployment Guide

This guide prepares the current MVP for Render backend deployment and Vercel frontend deployment. It does not add new business features.

## Deployment Targets

- Backend: Render Web Service
- Backend production URL: `https://careeros-ai-backend.onrender.com`
- Frontend: Vercel
- Frontend production URL: `https://careeros-ai-bay.vercel.app`
- Database: PostgreSQL / Supabase
- Storage: Supabase Storage private bucket, with local filesystem fallback for development

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

Current production backend:

```text
https://careeros-ai-backend.onrender.com
```

Render should expose the app on:

```text
PORT=10000
```

### Backend Environment Variables

Set these variables in Render:

```text
PROJECT_NAME=CareerOS AI API
DATABASE_URL=postgresql://...
JWT_SECRET_KEY=<strong-random-secret>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
BACKEND_CORS_ORIGINS=https://careeros-ai-bay.vercel.app,http://localhost:3000
SENTENCE_TRANSFORMERS_ENABLED=false
SENTENCE_TRANSFORMERS_MODEL_NAME=all-MiniLM-L6-v2
SENTENCE_TRANSFORMERS_LOCAL_FILES_ONLY=true
LOG_LEVEL=INFO
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<service-role-key>
SUPABASE_STORAGE_BUCKET=career-documents
PYTHON_VERSION=3.11.9
PORT=10000
```

Do not commit `.env`. Keep secrets only in Render environment variables.

### CORS

Local development origin:

```text
http://localhost:3000
```

Production frontend origin:

```text
https://careeros-ai-bay.vercel.app
```

`BACKEND_CORS_ORIGINS` supports multiple comma-separated origins. Avoid `*` in production because authenticated requests use JWT and should be limited to known frontend domains.

### Sentence Transformers on Render

CareerOS AI uses rule-based matching plus optional Sentence Transformers semantic similarity.

For Render free or small instances, keep:

```text
SENTENCE_TRANSFORMERS_ENABLED=false
SENTENCE_TRANSFORMERS_MODEL_NAME=all-MiniLM-L6-v2
SENTENCE_TRANSFORMERS_LOCAL_FILES_ONLY=true
```

With `SENTENCE_TRANSFORMERS_ENABLED=false`, the backend does not import or load `sentence-transformers` at startup or during matching. Matching falls back to rule-based scoring and the app can open its Render port quickly.

Only set `SENTENCE_TRANSFORMERS_ENABLED=true` when the deployment environment has enough memory/CPU for model load. If enabled, set `SENTENCE_TRANSFORMERS_MODEL_NAME=all-MiniLM-L6-v2` or another lightweight compatible model, and keep `SENTENCE_TRANSFORMERS_LOCAL_FILES_ONLY=true` unless you intentionally allow runtime model download.

### Supabase Storage

Production/beta uploads should use the private Supabase Storage bucket:

```text
career-documents
```

Required backend env vars:

```text
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<service-role-key>
SUPABASE_STORAGE_BUCKET=career-documents
```

Do not expose `SUPABASE_SERVICE_ROLE_KEY` to the frontend. Keep the bucket private. The backend uploads, downloads for analysis, and deletes objects with the service role key.

Object paths:

```text
users/{user_id}/resumes/{uuid}-{filename}
users/{user_id}/job-descriptions/{uuid}-{filename}
```

If `SUPABASE_URL` or `SUPABASE_SERVICE_ROLE_KEY` is missing, the backend falls back to local development storage under `backend/uploads`.

For existing databases created before Phase 5.5, run this once:

```sql
ALTER TABLE job_descriptions ADD COLUMN IF NOT EXISTS storage_path VARCHAR(500);
```

## Frontend on Vercel

Use `frontend/` as the Vercel project root.

Install/build commands can use Vercel defaults:

```bash
npm install
npm run build
```

Set this environment variable in Vercel:

```text
NEXT_PUBLIC_API_URL=https://careeros-ai-backend.onrender.com
```

Do not use `http://localhost:8000` in production. The frontend API clients read the backend URL from `NEXT_PUBLIC_API_URL`.

Current production frontend:

```text
https://careeros-ai-bay.vercel.app
```

## Production CORS Setup

Render `BACKEND_CORS_ORIGINS` must include the deployed Vercel domain:

```text
https://careeros-ai-bay.vercel.app
```

For local development, keep:

```text
http://localhost:3000
```

Recommended production value while still allowing local debugging:

```text
BACKEND_CORS_ORIGINS=https://careeros-ai-bay.vercel.app,http://localhost:3000
```

If the frontend can load but authenticated API calls fail in production, check this value first.

## Production Troubleshooting Notes

### Render Python 3.14 issue

Render may select a too-new Python version if runtime is not pinned. CareerOS AI should use:

```text
PYTHON_VERSION=3.11.9
```

The backend also includes `backend/runtime.txt` with:

```text
python-3.11.9
```

### Render port scan timeout

Render expects the app to bind to the configured port quickly. Use:

```text
PORT=10000
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

If Render reports port scan timeout, confirm the start command uses `$PORT` and that startup is not blocked by heavy model loading.

### Sentence Transformers on Render Free

Render Free can be too small for eager `sentence-transformers` or `torch` loading. Keep semantic matching disabled in production Free deployments:

```text
SENTENCE_TRANSFORMERS_ENABLED=false
SENTENCE_TRANSFORMERS_MODEL_NAME=all-MiniLM-L6-v2
SENTENCE_TRANSFORMERS_LOCAL_FILES_ONLY=true
```

With this setup, the app does not import/load Sentence Transformers at startup. Resume/JD matching falls back to rule-based scoring.

### CORS with Vercel

If login/register works locally but fails on Vercel, verify:

```text
BACKEND_CORS_ORIGINS=https://careeros-ai-bay.vercel.app,http://localhost:3000
NEXT_PUBLIC_API_URL=https://careeros-ai-backend.onrender.com
```

After changing Vercel env vars, redeploy the frontend.

## Deployment Checklist

Backend:

- Render service root is `backend/`.
- Build command is `pip install -r requirements.txt`.
- Start command is `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
- `/health` returns ok after deploy.
- Production health check works at `https://careeros-ai-backend.onrender.com/health`.
- `DATABASE_URL` points to PostgreSQL/Supabase.
- `JWT_SECRET_KEY` is strong and not committed.
- `BACKEND_CORS_ORIGINS` includes the Vercel production URL.
- `SENTENCE_TRANSFORMERS_ENABLED=false` for stable Render Free deploy unless model hosting is prepared.
- `SENTENCE_TRANSFORMERS_MODEL_NAME=all-MiniLM-L6-v2` as the default lightweight semantic model for local evaluation.
- `SENTENCE_TRANSFORMERS_LOCAL_FILES_ONLY=true` to avoid runtime model downloads when semantic matching is enabled.
- Supabase Storage env vars point to the private `career-documents` bucket.

Frontend:

- Vercel project root is `frontend/`.
- `NEXT_PUBLIC_API_URL=https://careeros-ai-backend.onrender.com`.
- `npm run build` passes locally before deploy.
- Login/register/dashboard calls work against deployed backend.

Production smoke test checklist lives in:

```text
docs/production-smoke-test.md
```

Before real beta:

- Verify upload/delete flow against Supabase Storage private bucket.
- Add database migrations before frequent schema changes.
- Review localStorage JWT risk for production security.
- Add monitoring/error tracking when traffic begins.
