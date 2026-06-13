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

## Deployment Overview

CareerOS AI được chuẩn bị để deploy theo hướng MVP production-ready:

- Backend deploy lên Render từ thư mục `backend/`.
- Frontend deploy lên Vercel từ thư mục `frontend/`.
- Database dùng PostgreSQL/Supabase qua `DATABASE_URL`.
- Frontend gọi backend qua `NEXT_PUBLIC_API_URL`.
- Backend CORS cấu hình bằng `BACKEND_CORS_ORIGINS`, hỗ trợ nhiều origin phân tách bằng dấu phẩy.

Tài liệu deployment chi tiết nằm ở `docs/deployment.md`.

Lưu ý hiện tại: upload CV/JD vẫn dùng local filesystem trong `backend/uploads`. Render filesystem không bền vững nếu không cấu hình persistent disk, nên production thật cần chuyển sang Supabase Storage ở phase sau.

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

Project đã có nền tảng kỹ thuật ban đầu: FastAPI backend, Next.js frontend, JWT authentication, career profile, upload CV PDF, lưu Job Description và Resume ↔ Job Matching MVP.

Phase hiện tại tập trung vào AI MVP có thể giải thích được: trích xuất text từ CV PDF, so khớp skill/keyword với Job Description và lưu lịch sử phân tích. Các module Career Diagnosis, Personalized Roadmap và Mock Interview AI chưa được triển khai ở bước này.

## Nguyên tắc phát triển

- Ưu tiên MVP chạy được, deploy được và có thể nhận feedback từ user thật.
- Giữ kiến trúc rõ ràng, đơn giản, dễ bảo trì.
- Không over-engineer trong giai đoạn đầu.
- Không tự ý thay đổi tech stack hoặc hướng kiến trúc nếu chưa có lý do rõ ràng.
- Production-ready không có nghĩa là phức tạp; ưu tiên nền tảng ổn định, bảo mật cơ bản, dễ triển khai và dễ mở rộng.
- Không hardcode secrets; dùng environment variables cho cấu hình nhạy cảm.
