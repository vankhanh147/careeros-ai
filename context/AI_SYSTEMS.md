# AI_SYSTEMS.md

## Current AI Philosophy

CareerOS AI đang dùng explainable AI MVP. Mục tiêu là tạo insight có thể kiểm chứng, không tạo “black box” phức tạp sớm.

AI hiện tập trung vào:

- Resume ↔ JD Matching
- Skill Gap Detection
- Improvement Plan
- Personalized Roadmap
- Mock Interview question generation and scoring

## Current AI Services

### `backend/app/services/resume_job_matcher.py`

Chức năng:

- Extract text từ CV PDF bằng `pypdf`.
- Extract text từ JD TXT bằng decode UTF-8/UTF-8-SIG/latin-1 fallback.
- Detect skills bằng dictionary + aliases.
- Tính keyword overlap.
- Tính length sanity.
- Tính semantic similarity bằng Sentence Transformers nếu model load được.
- Phân loại missing skills theo priority.
- Sinh skill gap summary, improvement plan, suggestions.
- Trả text previews để debug dữ liệu đã đọc.

Current skill matching:

- Case-insensitive.
- Dictionary gồm frontend, backend, fullstack, React, Next.js, Node.js, Express, FastAPI, Django, Flask, Python, Java, C#, ASP.NET Core, .NET, SQL, PostgreSQL, MySQL, MongoDB, Docker, Git, GitHub, REST API, JWT, authentication, TypeScript, JavaScript, HTML, CSS, Tailwind, Flutter, Firebase, Supabase, machine learning, AI, NLP và các skill mở rộng như Redis, GraphQL, OAuth, testing, CI/CD, cloud, SQLAlchemy, etc.
- Aliases hiện có: `js`, `ts`, `dotnet`, `postgres`, `asp net`, `asp.net`, `nextjs`, `next js`, `nodejs`, `node js`, `tailwind css`.

Scoring hiện tại:

- Nếu Sentence Transformers khả dụng:
  - skill max 45
  - keyword max 20
  - semantic max 25
  - length sanity max 10
- Nếu semantic không khả dụng:
  - skill max 65
  - keyword max 25
  - length sanity max 10
  - semantic_score = 0
- `final_score` capped at 100.

Semantic similarity:

- Model name: `all-MiniLM-L6-v2`.
- Env `SENTENCE_TRANSFORMERS_ENABLED` controls whether semantic matching is allowed. Keep it `false` on Render Free so the backend does not import/load `sentence-transformers` or torch before opening its port.
- Env `SENTENCE_TRANSFORMERS_LOCAL_FILES_ONLY` mặc định true and only matters when semantic matching is enabled.
- Nếu semantic matching disabled, model không có trong local cache hoặc import/load lỗi, service fallback về rule-based scoring.
- Không download model mặc định trong production/runtime nếu local-only true.

Skill gap priority:

- Role context detect từ JD: backend, frontend, fullstack, AI hoặc general.
- Missing skills được phân loại:
  - `high_priority`
  - `medium_priority`
  - `low_priority`
- Priority dựa trên skill có trong JD, frequency/keyword, và core skills theo role context.

### `backend/app/services/roadmap_generator.py`

Chức năng:

- Tạo roadmap rule-based từ selected analysis hoặc career profile.
- Timeline parser hỗ trợ số tuần/tháng tự nhiên:
  - `1 tuần` -> 1
  - `2 tuần` -> 2
  - `1 tháng` -> 4
  - `2 tháng` -> 8
  - fallback -> 6
- Roadmap item gồm:
  - `week`
  - `focus`
  - `skills`
  - `actions`
  - `expected_output`
- Nếu có analysis, ưu tiên `prioritized_missing_skills` và `improvement_plan`.
- Nếu không có analysis, dùng career profile và core skills theo target role.

### `backend/app/services/interview_generator.py`

Chức năng:

- Tạo 5 câu hỏi MVP.
- Question bank theo role:
  - backend
  - frontend
  - fullstack
  - ai
  - general
- Nếu có analysis, missing skills có thể inject skill-specific questions trước.
- `infer_target_role` ưu tiên target role explicit, sau đó career profile, fallback `General Software Developer`.

### `backend/app/services/interview_evaluator.py`

Chức năng:

- Chấm câu trả lời bằng expected keyword overlap.
- Keyword score tối đa 80.
- Length bonus tối đa 20.
- Feedback gồm điểm mạnh, keyword thiếu, gợi ý cải thiện.
- Session summary lấy average score các câu đã trả lời.

## Currently Used

- Rule-based scoring.
- Keyword overlap.
- Semantic similarity with Sentence Transformers when available.
- Sentence Transformers model `all-MiniLM-L6-v2`.
- Skill dictionary + aliases.
- Prioritized skill gaps.
- Rule-based improvement plan.
- Rule-based roadmap generator.
- Rule-based question bank.
- Rule-based interview scoring.

## Explicitly Not Used

- OpenAI API.
- LLM API.
- Fine-tuning.
- Custom model training.
- Voice AI.
- Video interview.
- OCR phức tạp.
- Agentic workflow.
- Multi-step autonomous AI agents.
- Heavy MLOps pipeline.

## AI Output Principles

- Luôn explainable: phải có breakdown, detected skills, preview text, suggestions.
- Luôn actionable: output cần có bước cải thiện cụ thể.
- Không tuyệt đối hóa score; score là tín hiệu hỗ trợ quyết định.
- Ưu tiên fallback an toàn hơn là làm app crash khi model semantic lỗi.

## Phase 6.5 Matching Scoring V2

Resume/JD matching now adds deterministic, explainable V2 signals on top of the existing rule-based matcher:

- Role-family detection for both CV and JD: backend, frontend, fullstack, ai/data, mobile, devops and general software.
- Stack group detection, for example python_backend, dotnet_backend, react_frontend, angular_frontend, mobile and cloud/devops groups.
- Role alignment scoring to penalize obvious frontend/backend mismatch and partially penalize same-role different-stack mismatch.
- Critical JD skill weighting so role-critical skills such as Python/FastAPI in a Python backend JD matter more than generic skills such as Git.
- Evidence-aware scoring that rewards matched skills appearing near project/experience/action evidence more than one-off keyword mentions.
- Confidence signal: high, medium or low based on CV length, JD length, detected skills and evidence richness.
- Semantic similarity remains optional through Sentence Transformers and is still disabled safely when `SENTENCE_TRANSFORMERS_ENABLED=false`.

Current scoring breakdown includes `skill_score`, `keyword_score`, `semantic_score`, `role_alignment_score`, `evidence_score`, `length_sanity`, `confidence` and `final_score`, plus debug fields for detected role families, role signals, stack groups, critical skills and scoring notes.

## Phase 6.6 CareerOS Benchmark V1

CareerOS AI now has an internal benchmark folder at `docs/benchmark-v1/` for Resume/JD Matching regression review.

Benchmark V1 records 10 beta cases U01-U10 covering exact backend fit, exact frontend fit, same-role different-stack, frontend/backend mismatch, backend/frontend mismatch, cross-domain transferable profiles and non-IT mismatch.

Before changing `backend/app/services/resume_job_matcher.py`, future agents should manually rerun U01-U10 and compare results with:

- V1 baseline scores in `expected_results_v1.md`.
- V2 target ranges in `expected_results_v2.md`.
- Evaluation rules in `evaluation_notes.md`.

This benchmark does not add a new AI module, does not use LLM APIs and does not require fine-tuning. It is a product regression guardrail for the existing deterministic matcher.

