# Năng lực hiện tại

## Sản phẩm

- **Authentication và ownership:** đăng ký, đăng nhập JWT, protected routes và kiểm soát dữ liệu theo user.
- **Career Profile:** lưu target role, level, skills, experience, projects, career goal và timeline.
- **Documents:** upload/xóa CV PDF; paste hoặc upload JD PDF/TXT; lưu file trong private Supabase Storage khi được cấu hình.
- **Resume ↔ JD Matching:** phân tích role, stack, critical skills, evidence, keyword và độ dài; trả score, breakdown, confidence và lịch sử.
- **Skill Gap:** phân loại kỹ năng thiếu theo high/medium/low priority và tạo improvement plan.
- **Resume Feedback:** gợi ý khoảng trống, wording, bullet rewrite và evidence cần bổ sung theo nguyên tắc không hallucinate.
- **Roadmap V2:** kế hoạch ngắn hạn với focus, bài thực hành, CV evidence, interview prep, priority và kết quả mong đợi.
- **Mock Interview V2:** question bank theo role/stack, adaptive selection, scoring và feedback có category.
- **Learning Loop Lite:** đánh dấu hoàn thành roadmap mới nhất, nhắc cập nhật CV và chạy lại matching.
- **Dashboard và Founder Insights:** tổng quan hành trình, next actions, funnel aggregate, feedback, missing skills và matching health.

## AI production

- Rule-based matcher V2.1 deterministic và explainable.
- Role-family/stack detection, mismatch penalty và critical skill weighting.
- Evidence-aware scoring và confidence signal.
- Taxonomy/Skill Graph hỗ trợ normalization và insight read-only.
- Rule-based fallback giúp analysis không phụ thuộc model nặng.

## AI hỗ trợ và evaluation

- Sentence Transformers optional, lazy-load, không gửi dữ liệu ra external API.
- Semantic insights và hybrid score candidate chạy song song, không thay điểm chính.
- ML V1 và hybrid model có pipeline train/evaluate offline.
- Benchmark U01–U10 và synthetic dataset phục vụ regression/evaluation.

## Dữ liệu và ML governance

- Dataset versioning, manifest, statistics và SHA256 fingerprint.
- Label Review QA, anonymization và promotion workflow.
- Training Job Contract và immutable model version.
- Model Registry Review Gate, comparison, decision record và release audit.
- Offline shadow harness, disagreement queue, human resolution export, QA bridge và promotion planning.

## Nền tảng vận hành

- Next.js frontend và FastAPI modular monolith.
- PostgreSQL/Supabase, SQLAlchemy và private Supabase Storage.
- Deployment beta trên Vercel và Render.
- CORS cấu hình theo environment; secrets không đưa ra frontend.
- Logging backend cơ bản và error response nhất quán.
- Backend test suite bao phủ các flow chính và nhiều workflow ML offline.

## Năng lực chưa được tuyên bố

CareerOS AI chưa có production ML inference, outcome prediction, OCR cho scanned CV, conversational interview, recruiter workflow hoặc multilingual UI. Những mục này không nên được mô tả như năng lực hiện hữu.
