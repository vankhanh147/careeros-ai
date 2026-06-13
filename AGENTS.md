# AGENTS.md

Tài liệu này hướng dẫn AI agents và contributors khi làm việc trên CareerOS AI.

CareerOS AI là một startup/product thực tế trong lĩnh vực AI hỗ trợ định hướng và phát triển nghề nghiệp công nghệ. Đây không phải demo sinh viên, không phải bài tập nhỏ và không nên được phát triển theo kiểu làm cho đủ chức năng bề mặt.

Mục tiêu là xây dựng một sản phẩm MVP có thể chạy được, deploy được, kiểm chứng với user thật và phát triển dần thành nền tảng production-ready.

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
