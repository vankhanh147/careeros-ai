# CURRENT_STATUS.md

Tài liệu này là snapshot trạng thái thật của CareerOS AI sau Phase 5.1. Future agents phải đọc file này cùng các file context khác trước khi làm feature mới.

## Product Status

CareerOS AI hiện là MVP web app có frontend Next.js và backend FastAPI. Sản phẩm đã có luồng user chính từ đăng ký/đăng nhập, nhập hồ sơ nghề nghiệp, quản lý CV/JD, chạy Resume ↔ JD Matching, xem skill gap, tạo roadmap học tập, luyện Mock Interview và xem dashboard tổng quan.

Project vẫn đang ở giai đoạn MVP-first, chưa phải production hardening đầy đủ. Các tính năng AI đang ưu tiên explainable/rule-based, có fallback rõ ràng, chưa dùng LLM API.

## Completed Phases

### Phase 3.1: Database + Authentication Foundation - Completed

- Backend kết nối PostgreSQL/Supabase qua `DATABASE_URL`.
- SQLAlchemy sync setup trong `backend/app/database.py` với `engine`, `SessionLocal`, `Base`, `get_db`.
- User model trong `backend/app/models/user.py`.
- JWT auth bằng `python-jose`; password hashing bằng `passlib[bcrypt]`.
- Endpoints:
  - `POST /api/auth/register`
  - `POST /api/auth/login`
  - `GET /api/auth/me`
- Auth dependency `get_current_user` bảo vệ các endpoint cần JWT.

### Phase 3.2: Frontend Auth UI + Protected Dashboard Shell - Completed

- Frontend dùng `NEXT_PUBLIC_API_URL`.
- API client cho auth trong `frontend/lib/api/auth.ts`.
- Token lưu localStorage qua `frontend/lib/auth/AuthContext.tsx`.
- Pages:
  - `/login`
  - `/register`
  - `/dashboard`
- Protected redirect: chưa login vào protected pages sẽ chuyển về `/login`.

### Phase 3.3: Career Profile Foundation - Completed

- Model `CareerProfile` liên kết 1-1 với `User` bằng unique `user_id`.
- Fields: `target_role`, `current_level`, `skills`, `experience_summary`, `projects_summary`, `career_goal`, `timeline`.
- Endpoints:
  - `GET /api/career-profile/me`
  - `PUT /api/career-profile/me`
- Frontend page `/profile` cho user nhập/cập nhật hồ sơ nghề nghiệp.

### Phase 3.4: Resume & Job Description Input Foundation - Completed

- Models:
  - `Resume`
  - `JobDescription`
- Resume upload PDF local vào `uploads/resumes/user_{id}`.
- JD có thể paste qua form; sau đó đã mở rộng thêm upload JD PDF/TXT.
- Endpoints:
  - `POST /api/resumes/upload`
  - `GET /api/resumes/me`
  - `DELETE /api/resumes/{id}`
  - `POST /api/job-descriptions`
  - `POST /api/job-descriptions/upload`
  - `GET /api/job-descriptions/me`
  - `PUT /api/job-descriptions/{id}`
  - `DELETE /api/job-descriptions/{id}`
- Frontend page `/documents` quản lý CV/JD, tạo/sửa/xóa JD, upload/xóa CV.

### Phase 4.1: Resume ↔ JD Matching MVP - Completed

- Model `MatchAnalysis` lưu kết quả phân tích cơ bản.
- Service `backend/app/services/resume_job_matcher.py`:
  - extract text PDF bằng `pypdf`
  - skill extraction rule-based
  - keyword overlap
  - length sanity
  - match score
- Endpoints:
  - `POST /api/analysis/resume-job-match`
  - `GET /api/analysis/history`
- Frontend page `/analysis` cho user chọn CV + JD, chạy matching, xem kết quả và lịch sử.

### Phase 4.1 Improvements: JD Upload + Debug Preview + Skill Dictionary - Completed

- JD upload hỗ trợ PDF/TXT, extract text và lưu vào `JobDescription.content`.
- Analysis response có debug fields:
  - `resume_text_preview`
  - `jd_text_preview`
  - `resume_detected_skills`
  - `jd_detected_skills`
  - `scoring_breakdown`
- Skill dictionary mở rộng và có aliases như `js -> javascript`, `ts -> typescript`, `postgres -> postgresql`, `dotnet -> .net`.

### Phase 4.2: Improve Resume ↔ JD Matching Quality - Completed

- Giữ rule-based skill matching.
- Bổ sung semantic similarity bằng Sentence Transformers model `all-MiniLM-L6-v2` nếu model load được.
- Có fallback rule-based nếu model không có trong local cache hoặc lỗi runtime.
- Scoring breakdown hiện gồm:
  - `skill_score`
  - `keyword_score`
  - `semantic_score`
  - `length_sanity`
  - `final_score`

### Phase 4.3: Skill Gap Detection + Improvement Plan MVP - Completed

- Analysis output có:
  - `skill_gap_summary`
  - `prioritized_missing_skills.high_priority`
  - `prioritized_missing_skills.medium_priority`
  - `prioritized_missing_skills.low_priority`
  - `improvement_plan`
- Priority dựa trên missing skills, role context từ JD và core skill sets backend/frontend/fullstack/AI.
- Frontend `/analysis` hiển thị skill gap summary, priority groups và kế hoạch cải thiện.

### Phase 4.3.1: Documents Management - Completed

- Backend thêm update/delete JD và delete Resume.
- User chỉ sửa/xóa dữ liệu của chính mình.
- Xóa resume sẽ xóa file local nếu tồn tại.
- Frontend `/documents` có edit mode cho JD, confirm delete, refresh state sau update/delete.
- Layout đã được fix để không tràn ngang với filename/path/URL dài.

### Phase 4.4: Personalized Roadmap MVP - Completed

- Model `LearningRoadmap`.
- Service `backend/app/services/roadmap_generator.py` tạo roadmap rule-based từ analysis hoặc career profile.
- Endpoints:
  - `POST /api/roadmaps/generate`
  - `GET /api/roadmaps/me`
  - `GET /api/roadmaps/{id}`
- Frontend page `/roadmap` cho chọn analysis, nhập timeline, generate roadmap, xem lịch sử.
- Timeline parser đã hỗ trợ input như `1 tuần`, `2 tuần`, `1 tháng`, `2 tháng`, fallback 6 tuần.

### Phase 4.5: Mock Interview AI MVP - Completed

- Models:
  - `InterviewSession`
  - `InterviewAnswer`
- Services:
  - `interview_generator.py`: question bank theo role và missing skills.
  - `interview_evaluator.py`: chấm điểm rule-based bằng keyword overlap + length bonus.
- Endpoints:
  - `POST /api/interviews/start`
  - `GET /api/interviews/me`
  - `GET /api/interviews/{id}`
  - `POST /api/interviews/{id}/answer`
  - `POST /api/interviews/{id}/finish`
- Frontend page `/interview` cho start session, trả lời từng câu, nhận feedback/score, finish session và xem lịch sử.

### Phase 4.6: AI MVP Polish & Dashboard Integration - Completed

- Backend endpoint `GET /api/dashboard/summary`.
- Dashboard summary trả user info, profile status, CV/JD counts, latest analysis, latest roadmap, latest interview, recommended next actions.
- Frontend `/dashboard` gom các module AI MVP vào một workspace tổng quan với cards và CTA rõ.

### Phase 5.1: UI/UX + Vietnamese Consistency Polish - Completed

- Frontend pages đã được polish tiếng Việt và trạng thái empty/loading/error:
  - `/`
  - `/login`
  - `/register`
  - `/dashboard`
  - `/profile`
  - `/documents`
  - `/analysis`
  - `/roadmap`
  - `/interview`
- Dashboard labels đã Việt hóa: “Không gian nghề nghiệp”, “Phân tích gần nhất”, “Roadmap gần nhất”, “Phiên phỏng vấn gần nhất”.
- Interview status frontend map `in_progress` thành “Đang luyện”, score null thành “Chưa hoàn thành”.
- Layout dùng `overflow-x-hidden`, `min-w-0`, `break-words`, `break-all` cho text/path/URL dài.
- Frontend `npm run lint` và `npm run build` pass sau Phase 5.1.

### Phase 5.2: Backend Validation + Error Handling + Logging Foundation - Completed

- Added consistent backend error response shape: `detail` string plus `code`.
- Added FastAPI exception handlers for app errors, HTTP errors, validation errors and unhandled errors.
- Added Python standard logging foundation with `LOG_LEVEL`.
- Added validation refinements for auth, career profile, JD, roadmap and interview schemas.
- Added logging for auth success/failure, upload rejection, analysis failure, roadmap generation failure and interview failure.
- Added safer local file delete checks for resume files and cleanup for invalid JD uploads.
- Kept API success contracts and database schema unchanged.

### Phase 5.3: Backend Tests Foundation - Completed

- Added pytest + FastAPI TestClient backend test suite under `backend/tests/`.
- Tests use isolated SQLite databases through `get_db` dependency override, not the real `.env` database.
- Upload folders are patched to temporary directories during tests.
- Added coverage for auth, career profile, documents, analysis, roadmap timeline parser, interview flow and dashboard summary.
- Checks passed: `python -m compileall app tests`, `pytest`, and `pip check`.

### Phase 5.4: Deployment Preparation - Completed

- Added Render deployment baseline for backend with `backend/render.yaml`.
- Added backend Python runtime recommendation in `backend/runtime.txt`.
- Added deployment guide in `docs/deployment.md`.
- Documented Render build/start commands and required backend environment variables.
- Documented Vercel frontend setup with `NEXT_PUBLIC_API_URL`.
- Removed frontend API client hardcoded localhost fallback outside `.env.example`; API clients now require `NEXT_PUBLIC_API_URL`.
- Documented CORS production setup and local upload storage limitation on Render.

### Phase 5.5: Supabase Storage Migration for Uploads - Completed

- Added backend Supabase Storage service using server-side `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, and `SUPABASE_STORAGE_BUCKET`.
- Resume uploads now store files in private Supabase Storage path `users/{user_id}/resumes/{uuid}-{filename}` when configured.
- JD uploads now store files in private Supabase Storage path `users/{user_id}/job-descriptions/{uuid}-{filename}` when configured.
- Local fallback under `backend/uploads` remains active when Supabase Storage env vars are missing.
- Resume analysis can download Supabase Storage objects into temp files when local files do not exist.
- Delete Resume/JD removes the Supabase object when `storage_path` exists.
- Added nullable `JobDescription.storage_path` for uploaded JD file tracking.
- Added mocked storage tests; pytest does not require real Supabase.

### Phase 5.6: Production Smoke Test & Deploy Notes - Completed

- Documented production backend URL: `https://careeros-ai-backend.onrender.com`.
- Documented production frontend URL: `https://careeros-ai-bay.vercel.app`.
- Updated deployment notes for Render env, Vercel env, production CORS and troubleshooting.
- Added production smoke test checklist in `docs/production-smoke-test.md`.
- Recorded known deployment caveats: Render Python runtime pin, `PORT=10000`, Sentence Transformers disabled on Render Free and Vercel CORS origin.

## Current Phase

Current phase: Phase 5 - Production Readiness. Phase 5.6 production smoke test and deploy notes are complete.

Đã hoàn thành UI/UX polish, backend validation/error/logging foundation, backend automated test foundation, deployment preparation và Supabase Storage migration. Các phần production readiness còn lại chưa hoàn thành đầy đủ: security review sâu hơn, monitoring/logging nâng cao, migration system và test coverage mở rộng cho edge cases.

## Next Recommended Phase

Recommended next: Phase 5.7 - Security review, migration system, monitoring and beta hardening.

Ưu tiên tiếp theo:

- Sửa các chuỗi tiếng Việt bị mojibake còn trong backend service/router.
- Mở rộng test coverage cho edge cases phức tạp hơn khi feature mới được thêm.
- Rà quyền truy cập user-owned resources.
- Rà file upload security và storage cleanup.
- Verify deploy thật trên Render/Vercel với Supabase PostgreSQL.
- Thêm migration system như Alembic trước khi schema thay đổi thường xuyên.

## Phase 6.1 Update: Beta Instrumentation & Feedback Foundation - Completed

Date: 2026-06-14

Phase 6.1 is complete.

- Added minimal PostgreSQL-backed usage tracking with `UsageEvent`.
- Tracked only core beta events: `resume_uploaded`, `jd_uploaded`, `analysis_generated`, `roadmap_generated`, `interview_started`, `interview_completed`, `feedback_submitted`.
- Added simple feedback storage with `UserFeedback`.
- Added `POST /api/feedback`.
- Added `GET /api/dashboard/usage-summary`.
- Added compact frontend feedback blocks after analysis result, roadmap generation and completed interview.
- No external analytics service, websocket, background queue or complex analytics dashboard was added.

Current phase:

- Current: Phase 6 - Beta Launch & Real User Feedback.
- Completed: Phase 6.1 Beta Instrumentation & Feedback Foundation.
- Next recommended: Phase 6.2 - run beta smoke tests with real users, review feedback signals and fix highest-impact friction.

## Phase 6.2 Update: UX Polish Based on Local Beta Testing - Completed

Date: 2026-06-14

Phase 6.2 focused on frontend UX polish only. No backend logic, API contract, AI feature or database schema was changed.

Completed polish:

- Landing page now explains the first 3 user steps: complete profile, add CV/JD, run AI MVP.
- Login/register forms trim input, show small hints and disable submit until required input is valid.
- Dashboard next actions now include a clear `Làm ngay` CTA mapped to the right product page.
- Profile page shows an onboarding hint when empty, adds field hints and disables save until the user enters at least one profile field.
- Documents page disables upload/save buttons until required file/content exists and adds file/JD input hints.
- Analysis, Roadmap and Interview pages have safer submit disabling while actions are running or required input is missing.
- Feedback block is less intrusive, explains why feedback matters and prevents repeated spam submissions after a successful feedback send.

Checks:

- `npm run lint` passed.
- `npm run build` passed.

Current phase:

- Current: Phase 6 - Beta Launch & Real User Feedback.
- Completed: Phase 6.2 UX Polish Based on Local Beta Testing.
- Next recommended: run local/production smoke test with a fresh beta user account and fix any observed friction.

## Phase 6.5 Update: Matching Scoring V2 - Completed

Date: 2026-06-14

Phase 6.5 improves Resume/JD Matching quality based on internal beta review without adding a new AI module, LLM API, fine-tuning or architecture changes.

Completed:

- Added role-family detection for CV and JD: backend, frontend, fullstack, ai/data, mobile, devops and general software.
- Added stack group detection and stack mismatch penalty.
- Added role alignment scoring so obvious role mismatch is penalized strongly.
- Added weighted critical JD skills so role-critical stack requirements count more than generic keywords.
- Added evidence-aware scoring for project/experience usage versus shallow keyword mentions.
- Added confidence signal: high, medium, low.
- Updated frontend analysis debug preview to show V2 scoring signals.
- Added backend tests for frontend/backend mismatch, same-role different-stack, exact backend fit and short-CV low confidence.

Checks passed: compileall, pytest, pip check, frontend lint and frontend build.

Current: Phase 6 - Beta Launch & Real User Feedback.
Next recommended: use production beta feedback to calibrate thresholds and collect exact expected/actual scores for future Matching V3.

## Phase 6.6 Update: CareerOS Benchmark V1 - Completed

Date: 2026-06-15

Phase 6.6 created the official internal benchmark documentation for Resume/JD Matching regression review. No backend feature, frontend feature, API contract, database schema or matcher logic was changed.

Completed:

- Added `docs/benchmark-v1/` as the internal benchmark source for U01-U10 beta cases.
- Recorded V1 scores and V2 target ranges for exact fit, same-role different-stack, role mismatch, cross-domain transferable and non-IT mismatch cases.
- Added manual evaluation rules for future matcher changes.
- Added `backend/scripts/run_benchmark_notes.py` to print the manual rerun checklist without calling API/database.

Current: Phase 6 - Beta Launch & Real User Feedback.
Next recommended: rerun U01-U10 with current production-like data and fill exact V2 scores before Matching V3 calibration.

## Phase 6.7 Update: Final Beta Stabilization - Completed

Date: 2026-06-15

Phase 6.7 focused on beta stabilization without adding a major feature, changing API contracts or changing the database schema.

Completed:

- Audited the core user flow from auth, profile, documents, analysis, roadmap, interview and dashboard.
- Added a shared frontend API error helper so network/API failures show friendlier messages across product flows.
- Polished dashboard hierarchy with MVP flow progress, refresh CTA and dynamic next actions based on actual user state.
- Reduced dashboard dependence on backend recommendation text matching for routing.
- Added `context/BETA_RELEASE_CHECKLIST.md` as the final manual beta release gate.

Current: Phase 6 - Beta Launch & Real User Feedback.
Next recommended: run the beta release checklist on production Render + Vercel with a fresh user account.

## Phase 7.1 Update: Production Beta Validation & Data Cleanup - Completed

Date: 2026-06-15

Phase 7.1 focused on production beta validation and small defensive cleanup. No new feature, database schema change, API contract change or backend logic change was introduced.

Completed:

- Audited the beta workflow across auth, profile, documents, analysis, roadmap, interview, dashboard and feedback.
- Fixed corrupted Vietnamese frontend API error/fallback messages by rewriting them with Unicode-safe strings.
- Fixed corrupted Vietnamese examples in `context/BETA_RELEASE_CHECKLIST.md`.
- Added `context/PHASE_7_1_VALIDATION_REPORT.md`.

Current readiness: beta-ready for a controlled production smoke test. Next recommended: run the production beta checklist with a fresh user, then continue to Phase 7.2 benchmark rerun and Matching V2.1 calibration.

## Phase 7.2 Update: Benchmark Rerun & Matching Calibration V2.1 - Completed

Date: 2026-06-15

Phase 7.2 reran CareerOS Benchmark U01-U10 against the current deterministic matcher using canonical benchmark texts derived from the documented beta cases. Sentence Transformers was disabled to match the Render Free production setting.

Completed:

- Filled V2.1 benchmark scores for U01-U10 in `docs/benchmark-v1/expected_results_v2.md`.
- Added `context/PHASE_7_2_CALIBRATION_REPORT.md`.
- Applied small matcher calibration only: negation-aware skill/evidence detection and specialized mobile/ai-data role selection when backend signals are only generic.
- Added regression tests for negated skill mentions and mobile cross-domain role detection.

Current readiness: Matching V2.1 is acceptable for controlled beta. Next recommended: collect real production disagreement cases before any further matcher tuning.

## Phase 7.3 Update: Resume Feedback & Rewrite Suggestions MVP - Completed

Date: 2026-06-15

Phase 7.3 adds deterministic resume improvement feedback after Resume/JD analysis. No LLM API, database schema change or breaking API contract was introduced.

Completed:

- Added additive `resume_feedback` output to analysis responses.
- Added template-based feedback groups: critical gaps, CV wording improvements, suggested bullet rewrites, missing evidence areas and recommended next edits.
- Added frontend `/analysis` section `Resume Improvement Suggestions`.
- Added benchmark sanity tests for U01, U02, U04 and U10.
- Added `context/PHASE_7_3_RESUME_FEEDBACK_REPORT.md`.

Current readiness: useful for controlled beta as safe CV edit guidance, not an automatic CV rewrite system.

## Phase 7.4 Update: Roadmap Quality V2 - Completed

Date: 2026-06-15

Phase 7.4 improves Personalized Roadmap quality while keeping the system rule-based, deterministic and schema-compatible. No LLM API, fine-tuning, database schema change or breaking API contract was introduced.

Completed:

- Roadmap items now include learning focus, practice task, CV evidence output, interview prep and priority.
- Roadmap generation from analysis now uses critical skills, confidence, resume feedback hints, role family and stack groups when available.
- Profile-only roadmap still works and clearly states lower personalization.
- Timeline parsing is more robust to Vietnamese and previously mojibake timeline strings.
- Frontend `/roadmap` displays the new item fields with a priority badge.
- Added/updated tests for Roadmap V2 item fields, priority and fallback behavior.
- Added `context/PHASE_7_4_ROADMAP_V2_REPORT.md`.

## Phase 7.5 Update: Mock Interview Question Bank V2 - Completed

Date: 2026-06-16

Phase 7.5 improves Mock Interview quality without LLM API, voice/video, database schema change or breaking API contract.

Completed:

- Expanded deterministic question bank for Backend .NET, Backend Node.js, Backend Python/FastAPI, Frontend React, AI/Data, Mobile Flutter and General software intern.
- Added adaptive question selection from missing/critical skills, latest roadmap interview prep, target role and stack context.
- Added additive response metadata for question reason, related skills, category and better answer hints.
- Improved answer feedback with categories such as `thiếu concept`, `thiếu ví dụ project`, `thiếu tradeoff`, `trả lời quá chung` and `có dấu hiệu hiểu đúng`.
- Polished frontend `/interview` to show role/stack context, why a question is asked, related skills and feedback category.
- Added `context/PHASE_7_5_INTERVIEW_V2_REPORT.md`.

## Phase 7.6 Update: User Learning Loop & Progress Tracking Lite - Completed

Date: 2026-06-16

Phase 7.6 adds a lightweight learning loop without turning CareerOS AI into a task manager and without changing the database schema.

Completed:

- Added roadmap item completion using the existing `LearningRoadmap.items` JSON payload.
- Added `PATCH /api/roadmaps/latest/items/{item_index}/completion` for the latest roadmap only.
- Frontend `/roadmap` now lets users mark current roadmap items complete/incomplete and shows a simple `Đã hoàn thành X/Y mục roadmap` summary.
- Dashboard summary now includes learning-loop signals: latest roadmap progress, `has_new_resume_after_analysis`, `should_rerun_analysis` and `learning_loop_summary`.
- Dashboard next actions now suggest rerunning analysis after a new CV upload or after roadmap progress, and suggest Mock Interview after roadmap creation.
- Added backend tests for completion updates and dashboard learning-loop signals.

Current readiness: CareerOS AI now has a simple return loop for beta users: learn from roadmap, update CV, rerun matching and practice interview.

## Phase 7.7 Update: Lightweight Founder Insights - Completed

Date: 2026-06-16

Phase 7.7 adds a lightweight founder/internal insights view without creating an analytics platform or changing the database schema.

Completed:

- Added founder-only endpoint `GET /api/founder/insights`, protected by JWT and `User.role` in `founder` or `admin`.
- Added hidden frontend page `/founder-insights` with aggregate cards/lists only.
- Aggregated product funnel counts, useful feedback by type, common missing skills, match health and learning-loop signals.
- Reused existing product data, `UsageEvent` and `UserFeedback`; no external analytics service or new event system was added.
- Added backend tests for founder auth, empty fallback and aggregate insight correctness.

Current readiness: founder can now answer where beta users are stuck and which MVP modules seem useful, without exposing PII or building a full analytics/admin product.

## Phase 8.1 Update: Career Taxonomy & Skill Graph Foundation - Completed

Date: 2026-06-19

Phase 8.1 creates reusable AI taxonomy foundations without changing production matcher behavior, database schema, API contract or UI.

Completed:

- Added `backend/app/ai/role_taxonomy.py` with normalized role definitions for Backend Developer, Frontend Developer, Fullstack Developer, Mobile Developer, AI / Machine Learning, Data Analyst, Data Engineer, DevOps, QA / Testing and Cybersecurity.
- Added `backend/app/ai/skill_graph.py` with skill aliases, categories and related skills for core authentication, frontend, backend, database, DevOps, mobile, AI/ML, data, testing and cybersecurity skills.
- Added `docs/ai-taxonomy/` documentation for role taxonomy and skill graph.
- Added `context/PHASE_8_1_TAXONOMY_REPORT.md`.

Current: Phase 8 - AI Intelligence Foundation.
Next recommended: Phase 8.2 should integrate taxonomy in read-only/parallel mode first, then compare against existing matcher outputs before changing production scoring.

## Language & Encoding Standard Update - Completed

Date: 2026-06-20

- Fixed Phase 8.1 taxonomy report and AI taxonomy docs to valid UTF-8 Vietnamese.
- Added `context/LANGUAGE_ENCODING_STANDARD.md` as the project-level standard for Vietnamese-first content and future i18n readiness.
- Added rules to avoid mojibake in new markdown, docs, reports and generated content.
- No app logic, API contract, database schema, matcher logic or UI behavior was changed.

## Phase 8.2 Update: Taxonomy Integration Read-only Mode - Completed

Date: 2026-06-20

Phase 8.2 integrates Career Taxonomy and Skill Graph as a read-only knowledge layer.

Completed:

- Added `backend/app/ai/taxonomy_insights.py` for skill alias normalization, role-family insight, stack group insight and related skill suggestions.
- Added additive `taxonomy_insights` metadata to Resume/JD analysis response.
- Roadmap generator now reads taxonomy to normalize aliases, reduce duplicate skills and suggest related skills lightly.
- Interview generator now normalizes missing/critical skill aliases before question selection.
- Benchmark safety rerun confirmed taxonomy metadata changes score delta by `0.0` for U01-U10 canonical reconstruction.
- No database schema, scoring formula, UI production flow, LLM, training or benchmark baseline change was introduced.

## Phase 8.3 Update: Semantic Matching Foundation - Completed

Date: 2026-06-20

Phase 8.3 adds a semantic matching foundation in parallel/evaluation mode.

Completed:

- Added `backend/app/ai/semantic_matcher.py` for lazy-loaded Sentence Transformers semantic insight.
- Added `SENTENCE_TRANSFORMERS_MODEL_NAME` with default `all-MiniLM-L6-v2`.
- Added additive `semantic_insights` metadata to Resume/JD analysis responses.
- Frontend `/analysis` now shows a small Vietnamese debug block for semantic status, similarity and notes.
- Added backend tests for disabled fallback, no import while disabled, load failure fallback, response metadata and final_score safety.
- No database schema, production scoring formula, benchmark baseline, LLM API, fine-tuning, vector database or infra change was introduced.

Current: Phase 8 - AI Intelligence Foundation.
Next recommended: Phase 8.4 should evaluate Hybrid Matching V3 only after semantic signals are benchmarked against U01-U10 with stable artifacts.
## Phase 8.4 Update: Hybrid Matching V3 Evaluation Mode - Completed

Date: 2026-06-21

Phase 8.4 adds a Hybrid Matching V3 candidate in evaluation/parallel mode.

Completed:

- Added `backend/app/ai/hybrid_evaluation.py` for a non-production hybrid score candidate.
- Analysis responses now include additive `hybrid_evaluation` metadata.
- Hybrid candidate combines rule-based score, semantic metadata, taxonomy alignment and confidence adjustment only for evaluation.
- `/analysis` shows a small Vietnamese debug block `Hybrid evaluation (thử nghiệm)`.
- Added `backend/scripts/run_hybrid_benchmark_notes.py` for manual U01-U10 review.
- Added backend tests for response presence, semantic-disabled fallback, taxonomy safety and final_score safety.
- No database schema, production `match_score`, production `final_score`, benchmark baseline, LLM, fine-tuning, vector database or infra change was introduced.

Current: Phase 8 - AI Intelligence Foundation.
Next recommended: collect benchmark observations for `hybrid_score_candidate` before any Phase 8.5 decision about production scoring.
## Phase 8.5 Update: Real Beta Dataset Foundation - Completed

Date: 2026-06-21

Phase 8.5 creates the data foundation for future trainable matching without changing production scoring, database schema, UI flow or existing API behavior.

Completed:

- Added `docs/datasets/` with dataset philosophy, benchmark/beta/training dataset definitions and standard evaluation formats.
- Added `docs/datasets/beta/` with U011-U013 template JSON files for future anonymized real beta cases.
- Added `docs/datasets/feedback_label_schema.json` for human feedback labels.
- Added `backend/app/ai/dataset_export.py` to export benchmark cases, feedback labels and analysis summaries as safe JSON.
- Added aggregate `feedback_labels` metadata to founder insights for total/agreed/disagreed feedback labels.
- Added backend tests for dataset export and updated founder insights tests.

Important boundary:

- No production `match_score` or `final_score` changed.
- No model training, LLM API, fine-tuning, vector database or new database schema was added.
- Dataset files do not contain real beta user data yet; U011-U013 are templates pending anonymized cases.

Current: Phase 8 - AI Intelligence Foundation.
Next recommended: collect anonymized beta artifacts and review disagreement cases before Phase 9.0 Trainable Matching Model.
## Phase 8.6 Update: Synthetic Dataset Generation Foundation - Completed

Date: 2026-06-21

Phase 8.6 creates a controlled synthetic dataset foundation for future trainable matching work while keeping production scoring unchanged.

Completed:

- Added `docs/datasets/synthetic/` with README, schema and generated dataset.
- Added 70 synthetic CV/JD matching cases across exact fit, same-role different-stack, role mismatch, cross-domain transferable, weak CV, keyword stuffing and non-IT mismatch groups.
- Added deterministic generator script `backend/scripts/generate_synthetic_dataset.py`.
- Added tests for generator size, group coverage, case IDs, labels and required fields.
- Updated dataset documentation and AI context.

Important boundary:

- Synthetic cases are not real beta data.
- No production `match_score` or `final_score` changed.
- No model training, LLM API, fine-tuning, vector database or database schema change was introduced.

Current: Phase 8 - AI Intelligence Foundation.
Next recommended: use synthetic data as evaluation supplement only, then combine with anonymized real beta cases before Phase 9.0 Trainable Matching Model.