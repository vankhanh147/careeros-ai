# CHANGELOG.md

This changelog summarizes completed CareerOS AI phases based on the current codebase and prior implementation history.

## Phase 0: Project Foundation

- Created initial repository structure.
- Added base docs: `README.md`, `PROJECT_CONTEXT.md`, `AGENTS.md`, `roadmap.md`.
- Established startup-ready, production-ready, MVP-first principles.

## Phase 1: Product & MVP Definition

- Defined CareerOS AI as an AI career development platform for technology careers.
- Defined MVP pillars: Career Diagnosis, Resume ↔ Job Matching, Skill Gap Detection, Personalized Roadmap, Mock Interview AI.
- Established non-goals: job board, generic chatbot, heavy AI training, recruiter dashboard, payment.

## Phase 2: Technical Scaffolding

- Scaffolded `backend/` with FastAPI.
- Scaffolded `frontend/` with Next.js, React, TypeScript, Tailwind CSS.
- Added `/health` endpoint.
- Configured CORS via environment variable.
- Added `.env.example` files.

## Phase 3.1: Database + Authentication Foundation

- Added PostgreSQL/Supabase connection via `DATABASE_URL`.
- Added SQLAlchemy setup.
- Added `User` model.
- Added JWT helpers and password hashing.
- Added auth endpoints: register, login, me.

## Phase 3.2: Frontend Auth UI + Protected Dashboard Shell

- Added auth API client.
- Added AuthContext with localStorage token.
- Added `/login`, `/register`, `/dashboard`.
- Added protected route behavior.

## Phase 3.3: Career Profile Foundation

- Added `CareerProfile` model and schemas.
- Added career profile endpoints.
- Added `/profile` UI for target role, current level, skills, experience, projects, career goal and timeline.

## Phase 3.4: Resume & Job Description Input Foundation

- Added `Resume` and `JobDescription` models.
- Added CV PDF upload and JD paste flow.
- Added `/documents` page.
- Added local file storage for uploaded CV files.

## Phase 4.1: Resume ↔ JD Matching MVP

- Added `MatchAnalysis` model.
- Added PDF text extraction with `pypdf`.
- Added rule-based skill extraction and scoring.
- Added analysis endpoints and `/analysis` UI.

## Phase 4.1 Improvements

- Added JD upload endpoint for PDF/TXT.
- Added debug preview fields in analysis response.
- Expanded skill dictionary and aliases.
- Frontend shows CV/JD previews, detected skills and scoring breakdown.

## Phase 4.2: Improve Matching Quality

- Added optional Sentence Transformers semantic similarity.
- Added fallback to rule-based scoring when semantic model unavailable.
- Added semantic score to frontend breakdown.
- Improved suggestions based on missing skills, semantic score and text length.

## Phase 4.3: Skill Gap Detection + Improvement Plan MVP

- Added prioritized missing skills.
- Added skill gap summary.
- Added improvement plan.
- Frontend displays priority groups and short-term plan.

## Phase 4.3.1: Documents Management

- Added update/delete JD endpoints.
- Added delete Resume endpoint.
- Added edit/delete controls on `/documents`.
- Fixed documents layout issues with long filenames and URLs.

## Phase 4.4: Personalized Roadmap MVP

- Added `LearningRoadmap` model.
- Added rule-based roadmap generator.
- Added roadmap endpoints and `/roadmap` UI.
- Fixed flexible timeline parser for week/month inputs.

## Phase 4.5: Mock Interview AI MVP

- Added `InterviewSession` and `InterviewAnswer` models.
- Added role-based question bank.
- Added keyword-overlap answer evaluator.
- Added interview endpoints and `/interview` UI.

## Phase 4.6: AI MVP Polish & Dashboard Integration

- Added `GET /api/dashboard/summary`.
- Integrated profile, documents, analysis, roadmap and interview into `/dashboard`.
- Added rule-based recommended next actions.

## Phase 5.1: UI/UX + Vietnamese Consistency Polish

- Polished main frontend pages with professional Vietnamese copy.
- Standardized empty/loading/error states.
- Fixed labels: Latest Matching/Roadmap/Interview, Status, Score, Actions, Skills, Expected output, Match Score.
- Improved responsive layout and long text wrapping.
- Frontend lint/build passed after changes.

## Long-Term Context System

- Added `context/` folder.
- Moved `PROJECT_CONTEXT.md` into `context/PROJECT_CONTEXT.md`.
- Added long-term memory files for status, architecture, AI systems, database, API contracts, UI/UX rules, decisions, known issues and changelog.
## Phase 5.2: Backend Validation + Error Handling + Logging Foundation

- Added `backend/app/core/errors.py` with app error class and FastAPI exception handlers.
- Added `backend/app/core/logging.py` using Python standard logging and `LOG_LEVEL`.
- Standardized backend error responses to `{detail, code}` while preserving `detail` as string.
- Refined Pydantic validation for auth, profile, JD, roadmap and interview requests.
- Added logging to auth, resume upload, JD upload, analysis, roadmap and interview flows.
- Added safer local upload cleanup/path checks.
- Updated backend README and context docs.

## Phase 5.3: Backend Tests Foundation

- Added `pytest` and `httpx` test dependencies.
- Added `backend/tests/` with FastAPI TestClient coverage for auth, career profile, documents, analysis, roadmaps, interviews and dashboard summary.
- Added isolated SQLite test database setup through dependency override.
- Patched upload roots to temporary test directories to avoid writing test files into persistent upload storage.
- Added roadmap timeline parser regression tests for `1 tuần`, `2 tuần`, `1 tháng` and empty timeline fallback.
- Backend checks passed: compileall, pytest and pip check.

## Phase 5.4: Deployment Preparation

- Added `backend/render.yaml` baseline for Render Web Service deployment.
- Added `backend/runtime.txt` with recommended Python runtime.
- Added `docs/deployment.md` with Render/Vercel deployment checklist.
- Updated backend README with Render build/start command, env vars, CORS and Sentence Transformers fallback notes.
- Updated frontend README with Vercel env setup.
- Updated root README with deployment overview.
- Centralized frontend API base URL in `frontend/lib/api/config.ts` and removed localhost fallback from API clients.

## Phase 5.5: Supabase Storage Migration for Uploads

- Added backend Supabase Storage service using private bucket access through service role key.
- Resume uploads now store objects at `users/{user_id}/resumes/{uuid}-{filename}` when Supabase env vars are configured.
- JD uploads now store objects at `users/{user_id}/job-descriptions/{uuid}-{filename}` when Supabase env vars are configured.
- Added local fallback under `backend/uploads` for development without Supabase env vars.
- Added `JobDescription.storage_path` to track uploaded JD objects for deletion.
- Analysis can download resume PDFs from Supabase Storage when local file paths do not exist.
- Delete Resume/JD removes the Supabase object when a storage path exists.
- Added mocked storage tests so pytest does not depend on real Supabase.

## Phase 5.6: Production Smoke Test & Deploy Notes

- Documented production backend URL: `https://careeros-ai-backend.onrender.com`.
- Documented production frontend URL: `https://careeros-ai-bay.vercel.app`.
- Updated `docs/deployment.md` with Render env, Vercel env, production CORS and deployment troubleshooting.
- Added `docs/production-smoke-test.md` with checklist for Register/Login, Profile, Upload CV/JD, Analysis, Roadmap, Mock Interview, Dashboard, Delete CV/JD and Supabase Storage upload/delete.
- Recorded troubleshooting notes for Render Python 3.14 issue, `PYTHON_VERSION=3.11.9`, `PORT=10000`, Sentence Transformers disabled on Render Free and Vercel CORS origin.

## Phase 6.1: Beta Instrumentation & Feedback Foundation

- Added `UsageEvent` model for minimal event tracking in PostgreSQL.
- Added `UserFeedback` model for useful/not useful feedback.
- Tracked core beta events for resume upload, JD upload, analysis generation, roadmap generation, interview start, interview completion and feedback submission.
- Added `POST /api/feedback`.
- Added `GET /api/dashboard/usage-summary`.
- Added compact frontend feedback UI after analysis, roadmap and completed interview outputs.
- Added backend tests for feedback creation, unauthorized feedback, usage summary and tracking flow.
