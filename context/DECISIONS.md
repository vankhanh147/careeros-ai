# DECISIONS.md

This file records technical and product decisions already made for CareerOS AI. Future work should not silently reverse these decisions.

## Product Decisions

- CareerOS AI is a real startup/product, not a student demo.
- MVP target users are technology learners, students, freshers, juniors and career switchers.
- Product value is employability improvement: understand current capability, compare with target jobs, identify skill gaps, build action plan and practice interviews.
- CareerOS AI is not a job board, not a generic chatbot and not a CV builder only.
- Prioritize actionable, explainable outputs over “fancy AI”.

## Architecture Decisions

- Use monorepo with `backend/`, `frontend/`, docs/context files.
- Backend is FastAPI + Python.
- Frontend is Next.js + React + TypeScript + Tailwind CSS.
- Database is PostgreSQL/Supabase via SQLAlchemy.
- Auth is JWT.
- Storage uses Supabase Storage private bucket for uploaded CV/JD files when configured, with local filesystem fallback for development.
- Deployment targets remain Vercel for frontend and Render for backend.
- Keep a modular monolith. Do not add microservices, queues, Kubernetes or distributed systems until real need.
- Do not introduce repository pattern yet; routers use SQLAlchemy Session directly for MVP simplicity.
- Do not add Docker unless explicitly requested.

## Backend Decisions

- SQLAlchemy sync session is used, not async SQLAlchemy.
- `Base.metadata.create_all(bind=engine)` is used on app startup for MVP schema creation.
- Required env vars:
  - `DATABASE_URL`
  - `JWT_SECRET_KEY`
- CORS origins are read from `BACKEND_CORS_ORIGINS`.
- User-owned resources are filtered by `current_user.id` in routers.
- Structured arrays are stored as JSON strings in text fields for MVP simplicity.
- No Alembic migration system yet.

## Frontend Decisions

- Use Next.js App Router.
- Use localStorage for JWT access token in MVP.
- Use simple React Context for auth state, no Redux/Zustand or complex state management.
- Use Tailwind utility classes directly.
- UI language is Vietnamese with natural technical terms preserved.
- Main UX is dark theme with cyan accents.
- Protected pages redirect unauthenticated users to `/login`.

## AI Decisions

- No OpenAI API or LLM API in current MVP.
- No fine-tuning.
- No custom training pipeline.
- Use rule-based matching first.
- Use Sentence Transformers only as lightweight semantic similarity enhancement.
- Default semantic model is `all-MiniLM-L6-v2`.
- Model loading is local-cache-first by default via `SENTENCE_TRANSFORMERS_LOCAL_FILES_ONLY=true`.
- If Sentence Transformers cannot load, fallback to rule-based score.
- Skill gap priority is rule-based from missing skills, role context and core skills.
- Roadmap generation is rule-based, not LLM generated.
- Mock Interview uses question bank + keyword scoring, not voice/video.

## Scope Decisions / Non-Goals

Do not add unless explicitly requested:

- Payment/billing.
- Recruiter dashboard.
- Admin panel.
- Job marketplace.
- Voice/video interview.
- Agentic workflow.
- Complex OCR.
- Heavy MLOps/training pipeline.
- Multi-tenant architecture.
- Event streaming.

## Documentation Decision

- `context/*.md` is the long-term memory and single source of truth for future phases.
- Agents should read `AGENTS.md`, `README.md`, `roadmap.md` and all relevant `context/*.md` before implementing new features.

## Phase 6.1 Beta Instrumentation Decisions

- Use existing PostgreSQL/Supabase database for beta instrumentation.
- Do not add external analytics services such as Mixpanel, PostHog, Google Analytics or Segment at this stage.
- Do not add websockets, background queues or event streaming for MVP beta tracking.
- Track only the agreed core events: `resume_uploaded`, `jd_uploaded`, `analysis_generated`, `roadmap_generated`, `interview_started`, `interview_completed`, `feedback_submitted`.
- Store only minimal metadata such as resource IDs, scores, timeline, target role and question count.
- Do not store CV/JD full content, file bytes, JWT tokens, secrets or unnecessary PII in usage metadata.
- Feedback uses a simple useful/not useful boolean, not 1-5 star ratings.
- Founder metrics remain simple counters through `GET /api/dashboard/usage-summary`; no analytics dashboard/charts yet.

## Phase 6.5 Matching Decisions

- Matching V2 remains deterministic and explainable; no LLM API, fine-tuning or new AI module was added.
- Role mismatch and stack mismatch are handled as scoring signals, not as hard rejection gates.
- Semantic similarity remains optional and must not be loaded at import or startup when disabled.
- Critical skill weighting should prioritize role-specific JD requirements over generic overlap.
- Confidence is a product trust signal and can cap low-information matches.

## Phase 6.6 Benchmark Decisions

- `docs/benchmark-v1/` is the official internal benchmark source for Resume/JD Matching changes.
- Future matcher changes should be checked against U01-U10 before shipping.
- V2 target ranges are broad product guardrails, not strict ML labels.
- Exact-fit cases should stay high, role mismatch and non-IT mismatch should stay lower, and same-role different-stack cases should remain in a realistic middle range.
- Benchmarking remains manual for now; no API automation, database schema change or new analytics system was added in Phase 6.6.

## Phase 7.2 Matching Calibration Decisions

- Matching V2.1 becomes the current benchmark baseline for Resume/JD Matching.
- Keep calibration pragmatic and deterministic; do not add a new model or LLM API to solve benchmark drift.
- Negated skill mentions should not count as skill evidence.
- Generic API/auth/database overlap should not automatically make mobile or data profiles look like backend profiles.
- Future matcher changes must compare against the V2.1 U01-U10 scores in `docs/benchmark-v1/expected_results_v2.md`.
