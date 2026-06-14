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
