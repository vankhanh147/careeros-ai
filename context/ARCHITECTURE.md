# ARCHITECTURE.md

## Overview

CareerOS AI hiện là monorepo MVP gồm:

- `frontend/`: Next.js + React + TypeScript + Tailwind CSS.
- `backend/`: FastAPI + Python + SQLAlchemy + Pydantic.
- Database: PostgreSQL/Supabase qua `DATABASE_URL`.
- Auth: JWT access token.
- AI services: Python services trong `backend/app/services`.
- File storage hiện tại: local filesystem trong `backend/uploads/...`; schema có `storage_path`/`file_url` để chuyển sang Supabase Storage sau.

Project đi theo kiến trúc monolith modular, chưa dùng microservices, queues, Kubernetes hoặc Docker.

## Backend Structure

Backend entrypoint: `backend/app/main.py`.

- App khởi tạo FastAPI với title từ env `PROJECT_NAME`.
- CORS đọc từ `BACKEND_CORS_ORIGINS`.
- `Base.metadata.create_all(bind=engine)` chạy trong lifespan để tạo bảng theo SQLAlchemy models.
- Routers được include trong `main.py`:
  - auth
  - dashboard
  - career_profile
  - resumes
  - job_descriptions
  - analysis
  - roadmaps
  - interviews
- Health check: `GET /health`.

Database setup:

- `backend/app/database.py`
- SQLAlchemy sync `create_engine`
- `SessionLocal = sessionmaker(...)`
- `get_db()` dependency yield sync `Session`

Config:

- `backend/app/core/config.py`
- Required env:
  - `DATABASE_URL`
  - `JWT_SECRET_KEY`
- Optional env:
  - `PROJECT_NAME`
  - `JWT_ALGORITHM`
  - `ACCESS_TOKEN_EXPIRE_MINUTES`
  - `BACKEND_CORS_ORIGINS`
  - `SENTENCE_TRANSFORMERS_LOCAL_FILES_ONLY`

## Frontend Structure

Frontend uses Next.js App Router.

Main pages:

- `/`: landing/entry page.
- `/login`: login form.
- `/register`: register form.
- `/dashboard`: integrated product dashboard.
- `/profile`: career profile form.
- `/documents`: CV/JD management.
- `/analysis`: Resume ↔ JD Matching and skill gap display.
- `/roadmap`: generate/view learning roadmaps.
- `/interview`: Mock Interview flow.

Auth state:

- `frontend/lib/auth/AuthContext.tsx`
- Access token stored in localStorage key `careeros_ai_access_token`.
- Protected pages redirect to `/login` when unauthenticated.

API clients:

- `frontend/lib/api/auth.ts`
- `frontend/lib/api/careerProfile.ts`
- `frontend/lib/api/documents.ts`
- `frontend/lib/api/analysis.ts`
- `frontend/lib/api/roadmaps.ts`
- `frontend/lib/api/interviews.ts`
- `frontend/lib/api/dashboard.ts`

## Main Flows

### Auth Flow

1. User registers via `/register`.
2. Frontend calls `POST /api/auth/register`.
3. Frontend logs in via `POST /api/auth/login`.
4. Backend returns JWT access token.
5. Frontend stores token in localStorage.
6. Protected API calls send `Authorization: Bearer <token>`.
7. Backend `get_current_user` verifies JWT and loads `User`.

### Career Profile Flow

1. User opens `/profile`.
2. Frontend calls `GET /api/career-profile/me`.
3. User updates profile fields.
4. Frontend calls `PUT /api/career-profile/me`.
5. Backend upserts 1 profile per user.

### Documents Flow

1. User uploads CV PDF on `/documents`.
2. Frontend calls `POST /api/resumes/upload` with multipart file.
3. Backend validates `.pdf`, max 5MB, writes local file to `uploads/resumes/user_{id}` and stores `Resume`.
4. User adds JD by paste or upload.
5. Paste calls `POST /api/job-descriptions`.
6. Upload calls `POST /api/job-descriptions/upload`, supports `.pdf` and `.txt`, max 5MB, extracts content into `JobDescription.content`.
7. User can update/delete JD and delete CV.

### Analysis Flow

1. User opens `/analysis`, chooses a Resume and JobDescription.
2. Frontend calls `POST /api/analysis/resume-job-match`.
3. Backend verifies both resources belong to current user.
4. If `Resume.extracted_text` is null, backend extracts PDF text and stores it.
5. `analyze_resume_job_match` computes skills, keywords, semantic score/fallback, skill gap, improvement plan.
6. Backend stores `MatchAnalysis` base fields and returns full response with debug preview and derived fields.
7. History endpoint recomputes derived/debug fields from stored resume/JD text when returning old analyses.

### Roadmap Flow

1. User opens `/roadmap`.
2. Frontend loads analysis history and roadmap history.
3. User optionally selects an analysis and timeline.
4. Frontend calls `POST /api/roadmaps/generate`.
5. Backend uses selected analysis if provided, otherwise career profile.
6. `roadmap_generator.py` parses timeline and creates weekly/step items.
7. Backend stores `LearningRoadmap.items` as JSON string.

### Interview Flow

1. User opens `/interview`.
2. User optionally selects analysis and target role.
3. Frontend calls `POST /api/interviews/start`.
4. Backend infers target role from explicit input or career profile.
5. `interview_generator.py` creates 5 questions from role question bank and missing skills.
6. User answers question by question using `POST /api/interviews/{id}/answer`.
7. `interview_evaluator.py` scores with keyword overlap + length bonus.
8. User finishes via `POST /api/interviews/{id}/finish`, backend averages scores and stores summary.

### Dashboard Flow

1. Frontend `/dashboard` calls `GET /api/dashboard/summary`.
2. Backend returns:
   - user info
   - career profile availability
   - CV/JD counts
   - latest analysis
   - latest roadmap
   - latest interview
   - recommended next actions
3. Frontend displays module cards and CTAs.

## Current Architecture Boundaries

- Backend owns auth, database writes, AI orchestration and resource authorization.
- Frontend owns UI state, redirects, forms, localStorage token and API client calls.
- AI logic stays in `backend/app/services`, not in routers or frontend.
- DB models stay in `backend/app/models`; Pydantic schemas stay in `backend/app/schemas`.
- No repository pattern currently; routers use SQLAlchemy Session directly for MVP simplicity.