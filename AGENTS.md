# AGENTS.md

Tài liệu này hướng dẫn AI agents và contributors khi làm việc trên CareerOS AI.

CareerOS AI là một startup/product thực tế trong lĩnh vực AI hỗ trợ định hướng và phát triển nghề nghiệp công nghệ. Đây không phải demo sinh viên, không phải bài tập nhỏ và không nên được phát triển theo kiểu làm cho đủ chức năng bề mặt.

Mục tiêu là xây dựng một sản phẩm MVP có thể chạy được, deploy được, kiểm chứng với user thật và phát triển dần thành nền tảng production-ready.


## Long-term project memory

- Luôn đọc `context/*.md` trước khi implement feature mới, sửa kiến trúc, thay đổi AI logic, database, API contract hoặc UI/UX flow.
- Xem `context/` là single source of truth cho trạng thái hiện tại, quyết định kỹ thuật, known issues và changelog của CareerOS-AI.
- Nếu codebase thực tế khác với tài liệu trong `context/`, phải ưu tiên xác minh bằng code thật, sau đó cập nhật lại file context liên quan.
- Sau mỗi phase hoặc thay đổi đáng kể, cập nhật tối thiểu `context/CURRENT_STATUS.md`, `context/CHANGELOG.md`, và các file context liên quan như `API_CONTRACTS.md`, `DATABASE_CONTEXT.md`, `AI_SYSTEMS.md`, `UI_UX_RULES.md`, `DECISIONS.md` hoặc `KNOWN_ISSUES.md`.

## Nguyên tắc cốt lõi

- Không over-engineer.
- Luôn ưu tiên MVP chạy được, deploy được và có user thật.
- Giữ project startup-ready và production-ready.
- Làm thay đổi nhỏ, rõ ràng, có mục đích.
- Không tự ý đổi kiến trúc hoặc tech stack nếu chưa được yêu cầu.
- Không thêm abstraction phức tạp khi chưa có nhu cầu thực tế.
- Ưu tiên code dễ đọc, dễ bảo trì, dễ debug.

## Tech Stack bắt buộc

- Backend dùng FastAPI và Python.
- Frontend dùng Next.js, React, TypeScript và Tailwind CSS.
- AI dùng Python.
- AI nên ưu tiên pretrained models, Sentence Transformers, scikit-learn và open-source models trước khi nghĩ đến giải pháp phức tạp hơn.
- Database dùng PostgreSQL / Supabase.
- Storage dùng Supabase Storage.
- Auth dùng JWT.
- Frontend deployment hướng tới Vercel.
- Backend deployment hướng tới Render.

## Không tự ý thêm

Không tự ý thêm các thành phần sau nếu chưa được yêu cầu rõ ràng:

- Microservices.
- Queues hoặc background job system phức tạp.
- Kubernetes.
- Payment hoặc billing flow.
- Recruiter dashboard.
- Admin system lớn.
- Event streaming.
- Multi-tenant architecture phức tạp.
- Model training pipeline nặng.

Nếu cần đề xuất một thành phần mới, phải giải thích rõ vấn đề thực tế mà nó giải quyết, tác động đến MVP và chi phí vận hành.

## Khi viết code

- Giữ kiến trúc rõ ràng theo từng domain/module.
- Đặt tên tốt, phản ánh đúng nghiệp vụ.
- Validate input ở backend.
- Xử lý lỗi rõ ràng, không để lỗi khó hiểu cho user.
- Không hardcode secrets, tokens, API keys hoặc credentials.
- Dùng environment variables cho cấu hình nhạy cảm.
- Không trộn logic AI, API, database và UI vào cùng một nơi.
- Viết code đủ đơn giản để có thể thay đổi khi feedback từ user thật xuất hiện.
- Ưu tiên test cho các luồng quan trọng của MVP.

## Định hướng product

CareerOS AI tập trung vào người dùng thật trong lĩnh vực công nghệ: sinh viên, người mới đi làm, junior developer, người chuyển ngành và người muốn phát triển sự nghiệp có định hướng hơn.

Các chức năng nên phục vụ trực tiếp cho giá trị cốt lõi:

- Hiểu năng lực hiện tại.
- So khớp với công việc hoặc vai trò mục tiêu.
- Phát hiện skill gap.
- Đề xuất roadmap cá nhân hóa.
- Hỗ trợ luyện phỏng vấn.

Mọi quyết định kỹ thuật nên giúp sản phẩm tiến gần hơn đến một MVP hữu ích, có thể triển khai và có thể học từ phản hồi thực tế.

## Language & Encoding Standard

- Toàn bộ markdown, docs, reports và generated content mới phải lưu UTF-8 chuẩn.
- Giai đoạn hiện tại ưu tiên tiếng Việt làm ngôn ngữ chính cho UI, docs, reports và generated content.
- Technical terms phổ biến như Backend, Frontend, Fullstack, REST API, JWT, Docker, FastAPI, Next.js, PostgreSQL, React, TypeScript, Machine Learning và AI có thể giữ nguyên khi tự nhiên.
- Không tạo mojibake trong file mới hoặc file đang sửa. Nếu thấy chuỗi tiếng Việt bị lỗi encoding, phải sửa ngay trong scope hiện tại.
- Chưa triển khai i18n cho tới khi có phase riêng. Text mới nên được đặt rõ ràng để sau này dễ migrate sang `vi` và `en`.
- Tham chiếu chuẩn chi tiết: `context/LANGUAGE_ENCODING_STANDARD.md`.
