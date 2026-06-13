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