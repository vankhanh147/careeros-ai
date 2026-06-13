# Roadmap

Roadmap này định hướng CareerOS AI như một startup/product thực tế trong lĩnh vực AI career development, tập trung vào MVP có thể triển khai, kiểm chứng với user thật và mở rộng có kiểm soát.

## Phase 0: Project Foundation

- Tạo cấu trúc repository ban đầu.
- Thiết lập tài liệu nền tảng: `README.md`, `AGENTS.md`, `PROJECT_CONTEXT.md`, `roadmap.md`.
- Xác định mindset phát triển: startup-ready, production-ready, MVP-first.
- Giữ project sạch, chưa scaffold Next.js hoặc FastAPI khi chưa chốt phạm vi MVP.

## Phase 1: Product & MVP Definition

- Xác định chân dung user mục tiêu trong lĩnh vực công nghệ.
- Làm rõ bài toán chính: Career Diagnosis, Resume ↔ Job Matching, Skill Gap Detection, Personalized Roadmap, Mock Interview AI.
- Viết user stories cho MVP v1.
- Xác định input/output chính của từng module.
- Phác thảo luồng trải nghiệm người dùng từ onboarding đến nhận kết quả AI.
- Xác định các chỉ số ban đầu để đo giá trị sản phẩm.

## Phase 2: Technical Scaffolding

- Scaffold frontend bằng Next.js, React, TypeScript và Tailwind CSS.
- Scaffold backend bằng FastAPI và Python.
- Thiết lập cấu trúc module backend rõ ràng.
- Thiết lập cấu trúc frontend theo hướng maintainable.
- Chuẩn bị cấu hình environment variables.
- Chuẩn bị kết nối PostgreSQL / Supabase.
- Chuẩn bị deployment baseline cho Vercel và Render.

## Phase 3: Core MVP

- Xây dựng authentication bằng JWT.
- Tạo user profile cơ bản.
- Tạo luồng nhập resume, kỹ năng, kinh nghiệm và mục tiêu nghề nghiệp.
- Tạo luồng nhập hoặc chọn job description mục tiêu.
- Xây dựng UI chính cho dashboard CareerOS AI.
- Lưu trữ dữ liệu người dùng trong PostgreSQL / Supabase.
- Lưu file cần thiết bằng Supabase Storage.

## Phase 4: AI MVP

- Xây dựng Career Diagnosis phiên bản đầu.
- Xây dựng Resume ↔ Job Matching bằng embedding hoặc scoring đơn giản.
- Xây dựng Skill Gap Detection dựa trên resume, skill set và job description.
- Tạo Personalized Roadmap từ skill gap và mục tiêu nghề nghiệp.
- Xây dựng Mock Interview AI ở mức MVP.
- Ưu tiên pretrained models và các phương pháp dễ kiểm soát trước khi mở rộng sang workflow phức tạp.

## Phase 5: Production Readiness

- Bổ sung validation input ở backend.
- Chuẩn hóa xử lý lỗi và response format.
- Bổ sung logging cơ bản.
- Viết test cho các luồng quan trọng.
- Kiểm tra bảo mật cơ bản: secrets, auth, file upload, quyền truy cập dữ liệu.
- Hoàn thiện cấu hình deployment cho frontend và backend.
- Chuẩn bị tài liệu vận hành tối thiểu.

## Phase 6: Beta Launch & Real User Feedback

- Triển khai bản beta cho nhóm user thật đầu tiên.
- Thu thập feedback về độ hữu ích của Career Diagnosis, matching, roadmap và Mock Interview AI.
- Đo các chỉ số sử dụng cơ bản.
- Ghi nhận lỗi, điểm nghẽn UX và các nhu cầu lặp lại.
- Ưu tiên cải tiến dựa trên tín hiệu thực tế thay vì giả định nội bộ.

## Phase 7: AI Expansion & Startup Scale

- Cải thiện chất lượng matching bằng Sentence Transformers và dữ liệu phản hồi.
- Mở rộng bộ kỹ năng, role taxonomy và career path trong lĩnh vực công nghệ.
- Tối ưu Personalized Roadmap theo cấp độ, mục tiêu và thời gian của user.
- Cải thiện Mock Interview AI theo từng role.
- Xem xét thêm analytics, admin tooling hoặc recruiter-facing features khi có nhu cầu rõ ràng.
- Mở rộng kiến trúc theo tải thật, không thêm hạ tầng phức tạp khi chưa cần.
