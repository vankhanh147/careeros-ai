# CareerOS AI

## Tên đề tài

Xây dựng nền tảng AI hỗ trợ định hướng nghề nghiệp trong lĩnh vực công nghệ - CareerOS AI

## Mô tả sản phẩm

CareerOS AI là nền tảng AI hỗ trợ người học và người đi làm trong lĩnh vực công nghệ hiểu rõ năng lực hiện tại, so khớp hồ sơ với vị trí mục tiêu, phát hiện khoảng trống kỹ năng và xây dựng lộ trình phát triển nghề nghiệp cá nhân hóa.

Sản phẩm được định hướng như một startup/product thực tế: có khả năng triển khai, mở rộng có kiểm soát, phục vụ người dùng thật và phát triển theo hướng MVP-first.

## Bài toán thực tế cần giải quyết

Người mới vào ngành, sinh viên công nghệ, junior developer và người chuyển hướng nghề nghiệp thường gặp các vấn đề sau:

- Không biết năng lực hiện tại phù hợp với vai trò công nghệ nào.
- Khó đánh giá resume có khớp với job description hay không.
- Không nhìn rõ skill gap giữa bản thân và vị trí mục tiêu.
- Thiếu roadmap học tập cá nhân hóa, thực tế và có thứ tự ưu tiên.
- Thiếu môi trường luyện phỏng vấn phù hợp với từng vai trò công nghệ.

CareerOS AI hướng tới việc biến dữ liệu nghề nghiệp rời rạc thành các insight rõ ràng, có thể hành động và có thể kiểm chứng bằng tiến bộ thật của người dùng.

## MVP v1

- Career Diagnosis: phân tích hồ sơ, kỹ năng, kinh nghiệm và mục tiêu để gợi ý hướng phát triển nghề nghiệp phù hợp.
- Resume ↔ Job Matching: so khớp resume với job description và đưa ra mức độ phù hợp.
- Skill Gap Detection: phát hiện kỹ năng còn thiếu so với vai trò hoặc công việc mục tiêu.
- Personalized Roadmap: tạo roadmap học tập và hành động cá nhân hóa.
- Mock Interview AI: hỗ trợ luyện phỏng vấn theo vai trò công nghệ cụ thể.

## Tech Stack

- Frontend: Next.js, React, TypeScript, Tailwind CSS
- Backend: FastAPI, Python
- Database: PostgreSQL / Supabase
- Storage: Supabase Storage
- Auth: JWT
- AI/ML: Python, Sentence Transformers, scikit-learn, open-source pretrained models
- Deployment: Vercel cho frontend, Render cho backend

## Cấu trúc thư mục

```text
CareerOS-AI/
├── backend/
├── frontend/
├── docs/
├── README.md
├── PROJECT_CONTEXT.md
├── AGENTS.md
├── roadmap.md
└── .gitignore
```

## Trạng thái hiện tại

Project đang ở giai đoạn khởi tạo nền tảng. Hiện tại chỉ có cấu trúc thư mục và tài liệu định hướng ban đầu.

Chưa scaffold Next.js hoặc FastAPI. Việc scaffold sẽ được thực hiện sau khi phạm vi MVP, kiến trúc cơ bản và luồng sản phẩm chính được xác định rõ.

## Nguyên tắc phát triển

- Ưu tiên MVP chạy được, deploy được và có thể nhận feedback từ user thật.
- Giữ kiến trúc rõ ràng, đơn giản, dễ bảo trì.
- Không over-engineer trong giai đoạn đầu.
- Không tự ý thay đổi tech stack hoặc hướng kiến trúc nếu chưa có lý do rõ ràng.
- Production-ready không có nghĩa là phức tạp; ưu tiên nền tảng ổn định, bảo mật cơ bản, dễ triển khai và dễ mở rộng.
- Không hardcode secrets; dùng environment variables cho cấu hình nhạy cảm.
