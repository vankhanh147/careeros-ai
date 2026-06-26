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

## Language & Encoding Decisions

- Current product language is Vietnamese-first until a dedicated i18n phase is implemented.
- New markdown, docs, reports and generated content must be saved as valid UTF-8.
- New UI/generated copy should be Vietnamese by default, while common technical terms can remain in English when natural.
- Do not introduce mojibake in new files or touched files. If encoding corruption is found in the current scope, fix it before finishing the phase.
- Future multilingual support should target `vi` and `en`, but language toggle/i18n infrastructure should wait for a dedicated phase to avoid premature complexity.
- Detailed standard lives in `context/LANGUAGE_ENCODING_STANDARD.md`.


## Phase 10.0 AI Training Infrastructure Decisions

- ML training infrastructure được đặt trong `backend/ml/` để tách khỏi production app code trong `backend/app/`.
- Dataset, model registry, experiment và evaluation report dùng JSON metadata trước, chưa cần database hoặc MLflow.
- Model registry record không đồng nghĩa model được productionize. Mọi model vẫn cần benchmark, beta validation và review trước khi ảnh hưởng user-facing score.
- Không dùng training infrastructure để thay `match_score` hoặc `final_score`.
- Real beta labels trong tương lai phải được ẩn danh và versioned thành dataset mới, không sửa im lặng dataset version cũ.

## Phase 10.1 Dataset Promotion Decisions

- Dataset version mới phải được tạo qua metadata draft, không sửa im lặng metadata version cũ.
- Dry-run là bước mặc định để review kế hoạch promote trước khi ghi file.
- `include_beta=true` bắt buộc có `beta_source_path` tồn tại.
- Nếu `require_human_review=true`, beta case phải có `human_review.reviewed=true` hoặc metadata tương đương.
- Beta source có dấu hiệu PII hoặc mojibake phải bị chặn trước khi promotion.
- Dataset draft không đồng nghĩa production-safe và không tự động train/evaluate model.

## Phase 10.2 Label Review Decisions

- Feedback thô không được dùng trực tiếp làm training label.
- Beta/training cases phải đi qua workflow `NEW -> ANONYMIZED -> UNDER_REVIEW -> APPROVED -> PROMOTED -> TRAINABLE`.
- `approved_for_training=true` chỉ hợp lệ khi case đã ẩn danh và status là `APPROVED`, `PROMOTED` hoặc `TRAINABLE`.
- Review metadata phải có reviewer, review time, label confidence, disagreement reason và notes.
- Label QA là offline metadata pipeline, không phải production API hoặc admin UI.
- Không promote hoặc train từ case có PII/mojibake hoặc thiếu human review metadata.

## Phase 10.3 Dataset Assembly Decisions

- Training dataset artifact chính cho phase tiếp theo là `backend/ml/datasets/training_dataset_v3.json`.
- Training/evaluation scripts tương lai nên đọc artifact đã assembly, không đọc trực tiếp từng source dataset rời rạc nếu không có lý do rõ.
- Artifact phải có manifest và SHA256 fingerprint.
- Assembly phải fail nếu phát hiện duplicate case ID, duplicate content hash, invalid label, source invalid, PII hoặc mojibake.
- Beta labels chỉ được đưa vào artifact khi đã approved, anonymized và có metadata review hợp lệ.

## Phase 10.4 Training Job Contract Decisions

- Training job mới chỉ được đọc dataset artifact đã assembly và manifest, không đọc source dataset rời rạc.
- `artifact_hash` trong manifest là validation gate bắt buộc.
- `dataset_version` phải khớp giữa config, artifact và manifest.
- `model_version` là immutable; nếu registry hoặc artifact directory đã tồn tại thì training job phải fail.
- Dry-run là cách verify mặc định trước khi ghi artifact.
- Registry draft từ training job luôn `production_safe=false` và không tự động được dùng cho runtime.
- Phase 10.4 ưu tiên LogisticRegression baseline để giữ training job nhẹ, deterministic và dễ kiểm thử.

## Phase 10.5 Model Registry Review Decisions

- Model registry draft không được xem là candidate chỉ vì training hoàn tất.
- Candidate criteria được cấu hình trong `model_review_config.json`, không hardcode vào production.
- Missing artifact, hash mismatch, missing evaluation/experiment và production boundary violation là FAIL.
- Metrics trong warning margin tạo WARNING; người review vẫn phải cân nhắc trước deployment decision.
- Write mode chỉ được cập nhật `candidate` hoặc `rejected`, luôn giữ `production_safe=false`.
- Không có auto promotion hoặc code path chuyển model sang production trong Phase 10.5.

## Phase 10.6 Deployment Decision Decisions

- Production baseline được định danh là `rule_based_matcher_v2.1`.
- Chỉ registry có `status=candidate` mới được so sánh; no-candidate mode chỉ được `keep_baseline`.
- Candidate classification metrics không được so sánh trực tiếp với production `match_score`.
- Thiếu benchmark/review evidence tạo kết luận `inconclusive`, không được coi là candidate tốt hơn.
- Write mode bắt buộc có reviewer và không overwrite decision record cũ.
- Mọi record luôn có `production_change_allowed=false`; Phase 10.6 không có deployment path.

## Phase 10.7 Release Audit Decisions

- Release checklist có 21 mục bắt buộc và mỗi mục phải có PASS/WARNING/FAIL cùng lý do.
- Thiếu quality command evidence tạo WARNING; script không tự khai command đã pass.
- Dataset hash, UTF-8, mojibake và PII được script kiểm tra trực tiếp.
- Write mode bắt buộc reviewer, không overwrite audit cũ và được phép ghi audit FAIL để giữ traceability.
- `production_change_allowed=false` là invariant bắt buộc.
- Release Ready offline không đồng nghĩa Production; runtime/shadow/deployment thuộc Phase 11 trở đi.
