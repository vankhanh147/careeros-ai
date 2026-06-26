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

## Phase 6.2: UX Polish Based on Local Beta Testing

- Polished landing onboarding with a clear 3-step first-use path.
- Improved auth form hints and disabled states.
- Added clear CTA links to dashboard recommended next actions.
- Improved profile empty/onboarding state and save button behavior.
- Improved documents upload/JD form hints and disabled states.
- Improved action button disabled states on analysis, roadmap and interview flows.
- Reduced feedback block intrusiveness and prevented repeated feedback submissions after success.
- Frontend checks passed: 
pm run lint`, 
pm run build`.

## Phase 6.5: Matching Scoring V2

- Added role-family detection for CV and JD.
- Added stack group detection and stack mismatch penalty.
- Added critical JD skill weighting.
- Added evidence-aware scoring for project/experience signals.
- Added confidence signal for analysis quality.
- Expanded scoring breakdown with role alignment, evidence score, confidence and debug signals.
- Updated `/analysis` debug preview to display V2 scoring signals.
- Added backend regression tests for beta-inspired mismatch and fit cases.

## Phase 6.6: CareerOS Benchmark V1

- Added `docs/benchmark-v1/` with official internal matcher benchmark documentation.
- Recorded 10 beta-inspired benchmark cases U01-U10 with V1 baseline scores and expected V2 behavior.
- Defined acceptable target ranges for exact fit, same-role different-stack, role mismatch, cross-domain transferable and non-IT mismatch cases.
- Added manual matcher evaluation rules and release guardrails.
- Added `backend/scripts/run_benchmark_notes.py` for a no-dependency manual rerun checklist.
- No application logic, API contract or database schema was changed.

## Phase 6.7: Final Beta Stabilization

- Added shared frontend API error handling helper for friendlier network/API errors.
- Updated frontend API clients to use the shared error handling path.
- Polished `/dashboard` with progress hierarchy, refresh CTA and dynamic next actions.
- Added `context/BETA_RELEASE_CHECKLIST.md` for final production beta readiness review.
- No backend feature, API contract or database schema was changed.

## Phase 7.1: Production Beta Validation & Data Cleanup

- Audited the current beta flow across auth, profile, CV/JD documents, analysis, roadmap, mock interview, dashboard and feedback.
- Fixed frontend API error/fallback messages that had lost Vietnamese accents.
- Fixed corrupted Vietnamese examples in `context/BETA_RELEASE_CHECKLIST.md`.
- Added `context/PHASE_7_1_VALIDATION_REPORT.md`.
- No backend logic, API contract, database schema or product feature was changed.

## Phase 7.2: Benchmark Rerun & Matching Calibration V2.1

- Reran U01-U10 benchmark using canonical benchmark texts and production-like semantic-disabled matcher mode.
- Updated `docs/benchmark-v1/expected_results_v2.md` with V2.1 scores, confidence, role families, stack groups, critical skills and notes.
- Updated `docs/benchmark-v1/benchmark_cases.md` with known V2.1 scores.
- Added `context/PHASE_7_2_CALIBRATION_REPORT.md`.
- Calibrated matcher lightly to ignore negated skill mentions such as 
o C#`, 
o React`, `without Docker` and `kh?ng c? backend`.
- Adjusted role-family detection so mobile and ai/data profiles are not mislabeled as backend when backend evidence is only generic API/auth/data overlap.
- Added backend regression tests for negation handling and mobile cross-domain matching.

## Phase 7.3: Resume Feedback & Rewrite Suggestions MVP

- Added template-based resume feedback to Resume/JD analysis output.
- Added additive `resume_feedback` response field without changing database schema.
- Feedback groups cover critical gaps, CV wording improvements, suggested bullet rewrites, missing evidence areas and recommended next edits.
- Frontend `/analysis` now displays `Resume Improvement Suggestions` on detailed analysis results.
- Added regression tests for U01, U02, U04 and U10 sanity checks.
- Added `context/PHASE_7_3_RESUME_FEEDBACK_REPORT.md`.

## Phase 7.4: Roadmap Quality V2

- Improved rule-based roadmap generator with action-oriented item fields: learning focus, practice task, CV evidence output, interview prep and priority.
- Roadmap generation from analysis now uses critical skills, confidence, resume feedback hints, role family and stack groups.
- Kept database schema unchanged by storing richer roadmap items in existing JSON `items`.
- Updated frontend `/roadmap` to display priority badge, practice task, CV evidence and interview prep.
- Added Roadmap V2 tests for practical output fields, priority handling and profile-only fallback.
- Added `context/PHASE_7_4_ROADMAP_V2_REPORT.md`.

## 2026-06-16 - Phase 7.5 Mock Interview Question Bank V2

- Expanded Mock Interview question bank by role/stack: Backend .NET, Backend Node.js, Backend Python/FastAPI, Frontend React, AI/Data, Mobile Flutter and General software intern.
- Added adaptive question selection using missing skills, analysis context and latest roadmap interview prep.
- Added additive interview answer metadata in API responses without database schema changes.
- Improved feedback classification and frontend `/interview` display.

## 2026-06-16 - Phase 7.6 User Learning Loop & Progress Tracking Lite

- Added lightweight roadmap item completion stored in existing roadmap JSON items.
- Added latest-roadmap-only completion endpoint: `PATCH /api/roadmaps/latest/items/{item_index}/completion`.
- Added roadmap progress summary on `/roadmap` and `/dashboard`.
- Added dashboard rerun signals for new CV uploads after analysis and partial roadmap completion.
- Added backend regression tests for roadmap completion and dashboard learning-loop signals.
- No database schema change, no new progress table and no gamification system were added.

## 2026-06-16 - Phase 7.7 Lightweight Founder Insights

- Added founder-only aggregate insights endpoint `GET /api/founder/insights`.
- Added hidden frontend page `/founder-insights` for product funnel, useful feedback, common missing skills, match health and learning-loop signals.
- Reused existing product tables, `UsageEvent` and `UserFeedback`; no external analytics service, charting system, new event system or database schema change was added.
- Added backend tests for founder access, empty data fallback and aggregation correctness.

## 2026-06-19 - Phase 8.1 Career Taxonomy & Skill Graph Foundation

- Added `backend/app/ai/role_taxonomy.py` as a shared static role taxonomy foundation.
- Added `backend/app/ai/skill_graph.py` as a shared static skill graph foundation.
- Added `docs/ai-taxonomy/` with role taxonomy and skill graph documentation.
- Added `context/PHASE_8_1_TAXONOMY_REPORT.md`.
- No production matcher logic, API contract, UI flow or database schema was changed.

## 2026-06-20 - Language & Encoding Standardization

- Fixed mojibake in `context/PHASE_8_1_TAXONOMY_REPORT.md`.
- Fixed mojibake in `docs/ai-taxonomy/README.md`, `docs/ai-taxonomy/role_taxonomy.md` and `docs/ai-taxonomy/skill_graph.md`.
- Added `context/LANGUAGE_ENCODING_STANDARD.md` for Vietnamese-first copy, UTF-8 markdown/report/docs rules and future i18n readiness.
- Updated AGENTS and DECISIONS with the new language/encoding rules.
- No backend/frontend runtime logic was changed.

## 2026-06-20 - Phase 8.2 Taxonomy Integration Read-only Mode

- Added `backend/app/ai/taxonomy_insights.py` as a read-only knowledge layer over role taxonomy and skill graph.
- Added additive `taxonomy_insights` field to analysis responses.
- Roadmap generation now uses taxonomy normalization and related skill hints without changing schema or architecture.
- Interview question selection now normalizes missing/critical skill aliases before matching question bank keys.
- Added backend tests for taxonomy normalization, analysis metadata, roadmap support and interview alias handling.
- Reran U01-U10 benchmark safety check with taxonomy metadata on/off; score delta was `0.0` for all cases.

## 2026-06-20 - Phase 8.3 Semantic Matching Foundation

- Added `backend/app/ai/semantic_matcher.py` as a lazy-loaded semantic insight service.
- Added additive `semantic_insights` metadata to analysis responses.
- Added `SENTENCE_TRANSFORMERS_MODEL_NAME` env documentation.
- Added a compact Vietnamese semantic insight block to `/analysis` debug preview.
- Added semantic fallback tests covering disabled mode, load failure and final_score safety.
- Added `backend/scripts/run_semantic_benchmark_notes.py` as a lightweight manual helper for U01-U10 semantic evaluation.
- Kept database schema, production scoring formula, benchmark baseline and API success fields backward-compatible.
## 2026-06-21 - Phase 8.4 Hybrid Matching V3 Evaluation Mode

- Added `backend/app/ai/hybrid_evaluation.py` for evaluation-only hybrid score candidates.
- Added additive `hybrid_evaluation` metadata to analysis responses.
- Added compact `/analysis` debug UI for Hybrid evaluation thử nghiệm.
- Added `backend/scripts/run_hybrid_benchmark_notes.py` for U01-U10 manual review.
- Added backend tests for hybrid response, semantic fallback, taxonomy safety and final_score safety.
- Kept production `match_score`, `final_score`, database schema and benchmark baseline unchanged.
## 2026-06-21 - Phase 8.5 Real Beta Dataset Foundation

- Added `docs/datasets/` with benchmark, beta and future training dataset definitions.
- Added `docs/datasets/beta/` with U011-U013 template files for future anonymized real beta cases.
- Added `docs/datasets/feedback_label_schema.json` for human feedback label format.
- Added `backend/app/ai/dataset_export.py` for safe JSON export of benchmark cases, feedback labels and analysis summaries.
- Added aggregate `feedback_labels` metadata to founder insights.
- Added backend tests for dataset export and updated founder insights aggregation tests.
- Kept production scoring, `match_score`, `final_score`, database schema, LLM usage and vector infrastructure unchanged.
## 2026-06-21 - Phase 8.6 Synthetic Dataset Generation Foundation

- Added `docs/datasets/synthetic/` for controlled synthetic CV/JD matching cases.
- Added `synthetic_case_schema.json` and generated `synthetic_cases.json` with 70 synthetic cases.
- Covered exact fit, same-role different-stack, role mismatch, cross-domain transferable, weak CV, keyword stuffing and non-IT mismatch groups.
- Added deterministic generator script `backend/scripts/generate_synthetic_dataset.py`.
- Added backend tests for synthetic dataset generator output and required fields.
- Kept production scoring, `match_score`, `final_score`, database schema, LLM usage and vector infrastructure unchanged.
## 2026-06-21 - Phase 8.7 Synthetic Dataset Quality Review

- Added `backend/scripts/validate_synthetic_dataset.py` to validate Synthetic Dataset V1.
- Added validator tests for generated dataset quality, duplicate case detection and PII detection.
- Added `docs/datasets/synthetic/DATASET_CARD.md`.
- Added `context/PHASE_8_7_DATASET_QUALITY_REPORT.md`.
- Validator confirmed 70 cases, balanced groups, valid labels/ranges and no blocking quality issues.
- No production scoring, database schema, UI, LLM usage, vector database or matcher logic was changed.
## 2026-06-22 - Phase 8.8 Synthetic Dataset Expansion V2

- Expanded synthetic dataset from 70 cases to 300 deterministic cases.
- Added seniority coverage for Intern, Fresher, Junior and Mid-level.
- Added role coverage for Backend, Frontend, Fullstack, Mobile, AI, Machine Learning, Data Analyst, Data Engineer, DevOps, QA and Cybersecurity.
- Added categories for strong evidence, career switch and missing critical skill cases.
- Added `docs/datasets/synthetic/STATISTICS.md`.
- Updated generator, validator, schema, dataset card and tests.
- Kept production scoring, `match_score`, `final_score`, database schema, LLM usage and vector infrastructure unchanged.

## 2026-06-22 - Phase 9.0 Trainable Matching Model V1

- Added `backend/app/ml/` for trainable matching prototype utilities.
- Added TF-IDF feature extraction and Logistic Regression classifier training.
- Added `backend/scripts/train_matching_model.py` to train from Synthetic Dataset V2 and save artifacts.
- Added model artifacts under `backend/models/`.
- Added `context/PHASE_9_0_MODEL_EVAL.md` and `context/PHASE_9_0_TRAINABLE_MODEL_REPORT.md`.
- Added additive `ml_evaluation` metadata to Resume/JD analysis responses.
- Added compact frontend `/analysis` block for ML evaluation in Vietnamese.
- Added backend tests for ML feature extraction, predictor fallback, mock artifact loading and analysis metadata.
- Kept production `match_score`, `final_score`, database schema, LLM usage, fine-tuning and vector infrastructure unchanged.

## 2026-06-22 - Phase 9.1 ML Benchmark & Disagreement Analysis

- Added `backend/scripts/run_ml_benchmark_analysis.py`.
- Evaluated ML V1 on U01-U10 benchmark cases using existing model artifacts.
- Generated `context/PHASE_9_1_ML_BENCHMARK_REPORT.md`.
- Generated `docs/datasets/synthetic/ml_error_analysis_v1.md`.
- Recorded disagreement status between rule-based score, hybrid candidate and ML prediction.
- Analyzed Synthetic Dataset V2 test-set confusion/error patterns without retraining.
- Kept production `match_score`, `final_score`, database schema, API contract, frontend UI, LLM usage, fine-tuning and vector infrastructure unchanged.

## 2026-06-25 - Phase 9.2 Feature Engineering & Hybrid Dataset V1

- Mở rộng `backend/app/ml/features.py` với structured hybrid feature extraction.
- Thêm script build dataset, validate dataset và train hybrid model.
- Sinh `docs/datasets/synthetic/hybrid_training_dataset.json` và `hybrid_feature_schema.json`.
- Train artifact offline riêng: `hybrid_matching_model.joblib`, `hybrid_matching_vectorizer.joblib`, `hybrid_model_metadata.json`.
- Tạo `context/PHASE_9_2_HYBRID_FEATURE_EVAL.md` và `context/PHASE_9_2_FEATURE_ENGINEERING_REPORT.md`.
- Hybrid feature model cải thiện synthetic test accuracy từ 0.733 lên 0.947 và giảm các lỗi boundary chính.
- Giữ nguyên production `match_score`, `final_score`, database schema, API contract, frontend UI, LLM usage, fine-tuning và vector infrastructure.

## 2026-06-26 - Phase 9.3 Hybrid Model Benchmark & Ablation Study

- Thêm `backend/scripts/run_hybrid_ablation_study.py` để chạy ablation study offline.
- So sánh text-only baseline, structured không có `rule_based_score`, structured core only và full hybrid.
- Sinh `context/PHASE_9_3_ABLATION_STUDY_REPORT.md` và `docs/datasets/synthetic/ablation_results_v1.md`.
- Sinh metadata riêng `backend/models/hybrid_ablation_metadata.json` mà không overwrite artifact Phase 9.0/9.2.
- Thêm tests cho ablation script, feature exclusion, metrics output và artifact safety.
- Giữ nguyên production `match_score`, `final_score`, database schema, API contract, frontend UI, LLM usage, fine-tuning và vector infrastructure.

## 2026-06-26 - Phase 10.0 AI Training Infrastructure Foundation

- Tạo ML workspace offline tại `backend/ml/` với configs, datasets, experiments, models, registry và reports.
- Thêm dataset metadata, model registry records, experiment template, evaluation report template và training config.
- Thêm `backend/app/ml/training_infra.py` để parse/validate metadata JSON.
- Thêm tests cho metadata load, dataset version parser, model registry parser, experiment parser và training config parser.
- Tạo docs `docs/ml/README.md`, `docs/ml/model_registry.md`, `docs/ml/dataset_versioning.md`, `docs/ml/experiment_tracking.md`.
- Tạo `context/PHASE_10_0_TRAINING_INFRA_REPORT.md`.
- Giữ nguyên production `match_score`, `final_score`, database schema, API production, UI production, LLM usage, fine-tuning và vector infrastructure.

## 2026-06-26 - Phase 10.1 Dataset Promotion Workflow

- Thêm `backend/ml/configs/dataset_promotion_config.json` làm config mẫu cho dataset promotion.
- Thêm `backend/scripts/promote_dataset_version.py` hỗ trợ `--dry-run` và write mode tạo metadata draft.
- Mở rộng `backend/app/ml/training_infra.py` với promotion config parser, validation target/source version, beta source validation, PII/mojibake scan và human review check.
- Tạo `docs/ml/dataset_promotion.md` và cập nhật `docs/ml/README.md`.
- Tạo `context/PHASE_10_1_DATASET_PROMOTION_REPORT.md`.
- Thêm tests cho promotion config parser, dry-run không tạo file, duplicate target version, missing beta path và missing human review metadata.
- Giữ nguyên production `match_score`, `final_score`, database schema, API production, UI production, LLM usage, fine-tuning và vector infrastructure.

## 2026-06-26 - Phase 10.2 Label Review & Quality Assurance Pipeline

- Thêm label review schema JSON và documentation cho review metadata.
- Chuẩn hóa workflow trạng thái `NEW -> ANONYMIZED -> UNDER_REVIEW -> APPROVED -> PROMOTED -> TRAINABLE`.
- Mở rộng `backend/app/ml/training_infra.py` với validator metadata review, status transition, anonymization, confidence, PII và mojibake checks.
- Thêm script `backend/scripts/validate_label_review_pipeline.py` để kiểm tra review cases offline.
- Thêm sample review cases template trong `backend/ml/reviews/sample_review_cases.json`.
- Thêm `docs/ml/label_quality.md` và report `context/PHASE_10_2_LABEL_QA_REPORT.md`.
- Giữ nguyên production `match_score`, `final_score`, database schema, API production, UI production, LLM usage, fine-tuning và vector infrastructure.
