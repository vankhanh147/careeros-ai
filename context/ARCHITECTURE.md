# ARCHITECTURE.md

## Overview

CareerOS AI hiện là monorepo MVP gồm:

- `frontend/`: Next.js + React + TypeScript + Tailwind CSS.
- `backend/`: FastAPI + Python + SQLAlchemy + Pydantic.
- Database: PostgreSQL/Supabase qua `DATABASE_URL`.
- Auth: JWT access token.
- AI services: Python services trong `backend/app/services`.
- File storage hiện tại: Supabase Storage private bucket khi `SUPABASE_URL` và `SUPABASE_SERVICE_ROLE_KEY` được cấu hình; local filesystem `backend/uploads/...` là fallback cho local development.

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
  - `LOG_LEVEL`
  - `SUPABASE_URL`
  - `SUPABASE_SERVICE_ROLE_KEY`
  - `SUPABASE_STORAGE_BUCKET`

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
3. Backend validates `.pdf`, max 5MB, uploads to Supabase Storage path `users/{user_id}/resumes/{uuid}-{filename}` when configured, otherwise writes local fallback to `uploads/resumes/user_{id}`.
4. User adds JD by paste or upload.
5. Paste calls `POST /api/job-descriptions`.
6. Upload calls `POST /api/job-descriptions/upload`, supports `.pdf` and `.txt`, max 5MB, uploads to Supabase Storage path `users/{user_id}/job-descriptions/{uuid}-{filename}` when configured, extracts content into `JobDescription.content`, and stores `JobDescription.storage_path`.
7. User can update/delete JD and delete CV; delete removes the Supabase object when a storage path exists.

### Analysis Flow

1. User opens `/analysis`, chooses a Resume and JobDescription.
2. Frontend calls `POST /api/analysis/resume-job-match`.
3. Backend verifies both resources belong to current user.
4. If `Resume.extracted_text` is null, backend extracts PDF text from local file or downloads the object from Supabase Storage into a temp file, then stores extracted text.
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

## Phase 6.1 Beta Instrumentation Architecture

CareerOS AI now has minimal beta instrumentation using the existing FastAPI + SQLAlchemy + PostgreSQL stack.

Backend additions:

- `backend/app/models/usage_event.py`
- `backend/app/models/user_feedback.py`
- `backend/app/schemas/feedback.py`
- `backend/app/schemas/usage.py`
- `backend/app/services/usage_tracking.py`
- `backend/app/routers/feedback.py`

Frontend additions:

- `frontend/lib/api/feedback.ts`
- `frontend/components/FeedbackBlock.tsx`

Tracking flow:

1. Backend tracks core product events only after successful user actions.
2. Events are stored in `usage_events` with `user_id`, `event_type`, small JSON metadata and `created_at`.
3. Tracked events are limited to resume upload, JD upload, analysis generation, roadmap generation, interview start, interview completion and feedback submission.
4. `GET /api/dashboard/usage-summary` returns simple founder metrics for the current user.

Feedback flow:

1. Frontend shows a compact feedback block after analysis result, roadmap result and completed interview.
2. User selects useful/not useful and can optionally add a short comment.
3. Frontend calls `POST /api/feedback`.
4. Backend stores `UserFeedback` and tracks `feedback_submitted`.

Safety boundary:

- No external analytics service.
- No websocket or queue.
- No CV/JD full content, file bytes, JWT token, secrets or unnecessary PII in usage metadata.
