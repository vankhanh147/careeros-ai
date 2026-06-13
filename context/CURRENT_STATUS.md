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

## Current Phase

Current phase: Phase 5 - Production Readiness.

Đã hoàn thành bước đầu của Phase 5 là UI/UX polish. Các phần production readiness còn lại chưa hoàn thành đầy đủ: backend validation tổng thể, response format chuẩn, logging, test suite, security review, deployment docs.

## Next Recommended Phase

Recommended next: Phase 5.2 - Backend Quality, Error Handling & Tests.

Ưu tiên tiếp theo:

- Sửa các chuỗi tiếng Việt bị mojibake còn trong backend service/router.
- Chuẩn hóa error messages và response format.
- Thêm test cho auth, documents, analysis, roadmap, interview, dashboard summary.
- Rà quyền truy cập user-owned resources.
- Rà file upload security và storage cleanup.
- Viết hướng dẫn deployment tối thiểu.