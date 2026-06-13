# KNOWN_ISSUES.md

Known limitations and fallback behavior in the current CareerOS AI MVP.

## Backend Text Encoding

Some Vietnamese strings inside backend services/routers currently appear mojibake in source/output, especially in:

- `backend/app/services/resume_job_matcher.py`
- `backend/app/services/roadmap_generator.py`
- `backend/app/services/interview_generator.py`
- `backend/app/services/interview_evaluator.py`
- some router error strings

Frontend Phase 5.1 cleaned the main UI copy, but backend-generated summaries/feedback may still display corrupted Vietnamese until backend strings are normalized to UTF-8.

Recommended fix: clean backend-generated Vietnamese strings in a dedicated polish pass without changing business logic.

## No Migration System Yet

- Database schema is created with `Base.metadata.create_all`.
- There is no Alembic migration setup.
- Adding/changing columns in existing databases may require manual migration.

## Local File Storage

- CV files are stored locally under `uploads/resumes/user_{id}`.
- JD upload files are stored locally under `uploads/job_descriptions/user_{id}`.
- Supabase Storage is planned but not implemented.
- Local storage is not ideal for Render deployments unless persistent disk is configured.

## Analysis Persistence Limitation

`MatchAnalysis` stores only base fields:

- score
- matched skills
- missing skills
- keyword overlap
- summary
- suggestions

Debug fields, semantic breakdown, prioritized skill gaps and improvement plan are recomputed on response/history from current resume/JD text. This means old history can change if the underlying JD/resume text or AI logic changes.

## Sentence Transformers Fallback

- `sentence-transformers` dependency exists.
- Model: `all-MiniLM-L6-v2`.
- Default env is `SENTENCE_TRANSFORMERS_LOCAL_FILES_ONLY=true`.
- If the model is not cached locally, semantic score is unavailable and system falls back to rule-based scoring.
- This is intentional for deploy stability, but matching quality depends on model availability.

## PDF/Text Extraction Limits

- CV extraction uses `pypdf` only.
- No OCR for scanned/image PDFs.
- JD upload supports PDF/TXT only, not DOCX.
- Extracted text quality depends on PDF structure.

## Auth Storage Limitation

- Frontend stores JWT in localStorage for MVP simplicity.
- This is acceptable for early MVP but should be revisited for production security.

## Test Coverage Gap

Current request history indicates lint/build checks were run, but there is no comprehensive automated backend/frontend test suite yet.

High-priority test targets:

- auth register/login/me
- protected resource ownership
- upload CV/JD validation
- analysis with sample CV/JD
- roadmap generation timeline parser
- interview start/answer/finish
- dashboard summary for empty and populated users

## Dashboard Summary Recompute

Dashboard latest analysis calls matcher logic to derive skill gap summary when possible. If matcher throws, it falls back to stored analysis summary.

## Career Diagnosis Not Separately Implemented

The roadmap still lists Career Diagnosis as MVP v1 feature, but current codebase does not have a standalone Career Diagnosis module/page. Some diagnosis-like value is covered indirectly by career profile, analysis, skill gap, roadmap and interview.

## Logging Limitation

Phase 5.2 added Python standard logging for startup, auth, upload, analysis, roadmap and interview events. There is still no request ID middleware, structured JSON logging, external error tracking or monitoring setup yet.

## No Deployment Config Finalization Yet

Vercel/Render are target platforms, but production deployment docs/config are not complete in the current codebase.
## Error Handling Limitation

Phase 5.2 adds consistent `{detail, code}` error responses. Existing frontend remains compatible because `detail` is still a string. Error messages are intentionally short English strings for backend consistency. Full i18n of backend error messages is not implemented.