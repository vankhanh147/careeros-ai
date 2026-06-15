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

## Storage Limitations

- Phase 5.5 wires Resume and uploaded JD files to Supabase Storage when `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are configured.
- Local storage under `backend/uploads` remains as a development fallback when Supabase env vars are missing.
- Existing databases created before Phase 5.5 need a one-time migration: `ALTER TABLE job_descriptions ADD COLUMN IF NOT EXISTS storage_path VARCHAR(500);`.
- There is still no Alembic migration system, so production schema changes must be applied manually for now.

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
- Default production env should keep `SENTENCE_TRANSFORMERS_ENABLED=false` on Render Free to avoid importing/loading torch and the semantic model before the app can open its port.
- `SENTENCE_TRANSFORMERS_LOCAL_FILES_ONLY=true` prevents runtime model downloads when semantic matching is enabled.
- If semantic matching is disabled or unavailable, semantic score is unavailable and the system falls back to rule-based scoring.
- This is intentional for deploy stability, but matching quality depends on model availability when semantic matching is enabled.

## PDF/Text Extraction Limits

- CV extraction uses `pypdf` only.
- No OCR for scanned/image PDFs.
- JD upload supports PDF/TXT only, not DOCX.
- Extracted text quality depends on PDF structure.

## Auth Storage Limitation

- Frontend stores JWT in localStorage for MVP simplicity.
- This is acceptable for early MVP but should be revisited for production security.

## Test Coverage Limitations

Phase 5.3 added the backend test foundation with pytest and FastAPI TestClient. The suite covers the most important happy paths and baseline failure paths:

- auth register/login/me and duplicate/wrong-password errors
- career profile upsert/get
- CV upload validation and delete
- JD create/update/delete/upload validation
- basic ownership protection for deleting another user's JD
- Resume ↔ JD analysis response shape and missing resume failure
- roadmap generation from profile/analysis and timeline parser regression cases
- interview start/answer/finish
- dashboard summary for new and populated users

Remaining gaps:

- No frontend automated tests yet.
- No browser/E2E test suite yet.
- Backend tests use SQLite, so PostgreSQL-specific behavior is not fully covered.
- File upload tests use minimal generated PDFs; complex real-world PDF extraction edge cases are not covered.
- Supabase Storage behavior is covered with mocked storage service tests, but not with live Supabase integration tests.

## Dashboard Summary Recompute

Dashboard latest analysis calls matcher logic to derive skill gap summary when possible. If matcher throws, it falls back to stored analysis summary.

## Career Diagnosis Not Separately Implemented

The roadmap still lists Career Diagnosis as MVP v1 feature, but current codebase does not have a standalone Career Diagnosis module/page. Some diagnosis-like value is covered indirectly by career profile, analysis, skill gap, roadmap and interview.

## Logging Limitation

Phase 5.2 added Python standard logging for startup, auth, upload, analysis, roadmap and interview events. There is still no request ID middleware, structured JSON logging, external error tracking or monitoring setup yet.

## Deployment Limitations

Phase 5.4 adds deployment documentation and baseline Render/Vercel configuration. Phase 5.6 records the current production endpoints and smoke test checklist.

Current production endpoints:

- Backend: `https://careeros-ai-backend.onrender.com`
- Frontend: `https://careeros-ai-bay.vercel.app`

Known production deployment caveats:

- Render should pin Python with `PYTHON_VERSION=3.11.9` or `backend/runtime.txt` containing `python-3.11.9`; newer Python such as 3.14 can break dependency compatibility.
- Render should use `PORT=10000` and start with `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
- Render Free should keep `SENTENCE_TRANSFORMERS_ENABLED=false` to avoid port scan timeout from heavy model/torch loading.
- Production CORS must include `https://careeros-ai-bay.vercel.app`; otherwise Vercel frontend calls can fail even when backend health check passes.
- `docs/production-smoke-test.md` is currently a manual checklist; there is no automated production E2E smoke suite yet.
## Error Handling Limitation

Phase 5.2 adds consistent `{detail, code}` error responses. Existing frontend remains compatible because `detail` is still a string. Error messages are intentionally short English strings for backend consistency. Full i18n of backend error messages is not implemented.

## Phase 6.2 UX Notes

No new known backend or schema issues were introduced in Phase 6.2.

Remaining UX/testing limitations:

- There is still no automated frontend E2E/browser test suite.
- Phase 6.2 polish was verified through `npm run lint` and `npm run build`; full user-path validation should still be done manually with the production smoke checklist.

## Phase 6.5 Matching V2 Limitations

- Role-family and stack detection are heuristic and dictionary-based, so unusual titles or uncommon technologies can still be misclassified.
- Evidence-aware scoring uses text-window heuristics around project/experience terms; it is not a true semantic proof of real experience.
- Thresholds for role alignment, stack penalty and confidence were calibrated pragmatically from beta patterns, not from a labeled dataset.
- `MatchAnalysis` still stores only base fields, so V2 debug fields are recomputed for history from current matcher logic.
- Frontend debug labels for new V2 technical scoring fields intentionally use short English technical labels to avoid encoding regressions in the current source state.

## Phase 6.7 Remaining Beta Limitations

- Phase 6.7 improved frontend API error messages, but there is still no automated browser/E2E suite.
- Dashboard has a retry CTA; other data-heavy pages still rely mostly on page reload/navigation after a failed initial load.
- Production beta release still requires manual validation using `context/BETA_RELEASE_CHECKLIST.md`.
- No new monitoring or external error tracking was added.

## Phase 7.1 Validation Notes

Phase 7.1 fixed frontend API error message encoding and beta checklist encoding. Remaining beta limitations are unchanged: no automated E2E suite, no Alembic migration system, manual production smoke test still required, and some backend-generated Vietnamese strings may still need a dedicated cleanup pass.

## Phase 7.3 Resume Feedback Limitations

- Resume feedback is template-based and heuristic. It is useful for MVP guidance but not a full CV rewrite tool.
- Suggestions depend on extracted CV text quality; scanned PDFs or poor PDF extraction can reduce accuracy.
- The engine does not yet point to exact original CV bullet lines.
- The engine avoids hallucination by using conditional wording for missing skills, but users must still verify suggestions against their real experience.
- `resume_feedback` is recomputed like other analysis debug fields because `MatchAnalysis` still stores only base analysis fields.
