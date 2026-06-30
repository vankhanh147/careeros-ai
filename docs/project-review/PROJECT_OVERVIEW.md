# Tổng quan dự án

## CareerOS AI là gì?

CareerOS AI là nền tảng career intelligence dành cho người theo đuổi nghề nghiệp công nghệ. Sản phẩm biến CV, Job Description và mục tiêu nghề nghiệp thành các insight có thể hành động: mức độ phù hợp, khoảng trống kỹ năng, cách cải thiện CV, kế hoạch học tập và bài luyện phỏng vấn.

Sản phẩm được xây theo mindset startup: giải quyết một hành trình thật, triển khai được cho người dùng beta, thu tín hiệu sử dụng và cải thiện theo bằng chứng. CareerOS AI không được định vị như công cụ “chấm CV bằng AI” đơn lẻ, mà như một vòng lặp phát triển năng lực nghề nghiệp.

## Người dùng mục tiêu

- Sinh viên công nghệ và ứng viên Intern/Fresher cần xác định khoảng cách tới vị trí đầu tiên.
- Junior Developer muốn chuyển stack, nâng vai trò hoặc chuẩn bị cho JD cụ thể.
- Career switcher cần hiểu kỹ năng chuyển đổi nào có giá trị và khoảng trống nào là cốt lõi.
- Người tự học cần một thứ tự hành động rõ hơn thay vì danh sách kỹ năng chung chung.

## Vấn đề cốt lõi

Ứng viên thường có dữ liệu nhưng thiếu cách diễn giải: CV mô tả những gì đã làm, JD mô tả kỳ vọng tuyển dụng, còn khóa học và câu hỏi phỏng vấn nằm rời rạc. Họ khó trả lời năm câu hỏi liên tiếp:

1. Tôi đang phù hợp với vai trò nào?
2. CV này khớp JD đến đâu?
3. Tôi thiếu kỹ năng hay thiếu bằng chứng?
4. Tôi nên học và thực hành gì trước?
5. Làm sao kiểm tra mình đã tiến bộ?

CareerOS AI kết nối các câu hỏi đó thành một luồng duy nhất.

## Giá trị sản phẩm hiện tại

- **Rõ khoảng cách:** Matching và skill gap cho biết điểm phù hợp, kỹ năng đã khớp, kỹ năng còn thiếu và nguyên nhân.
- **Rõ cách sửa:** Resume Feedback đưa ra đề xuất có điều kiện, không tự bịa kinh nghiệm hoặc thành tích.
- **Rõ việc cần làm:** Roadmap V2 chuyển skill gap thành bài thực hành, minh chứng CV và câu hỏi phỏng vấn.
- **Rõ cách luyện:** Mock Interview V2 chọn câu hỏi theo role, stack và điểm yếu đã phát hiện.
- **Có vòng lặp:** Người dùng đánh dấu tiến độ, cập nhật CV rồi chạy lại matching thay vì nhận kết quả một lần.

## Triết lý AI

AI production hiện ưu tiên deterministic và explainable. Rule-based matcher V2.1 kết hợp kỹ năng, keyword, role alignment, stack alignment, evidence và confidence. Sentence Transformers có thể bổ sung semantic insight khi môi trường cho phép, nhưng không làm hệ thống mất khả năng vận hành khi model không tải được.

Các model ML đã được thử nghiệm offline, song chưa thay thế điểm production. Đây là lựa chọn có chủ đích: tín nhiệm của người dùng quan trọng hơn việc gắn nhãn “AI” cho một mô hình chưa đủ dữ liệu thực.

## Trạng thái hiện tại

CareerOS AI đã có frontend Next.js, backend FastAPI, PostgreSQL/Supabase, Supabase Storage, JWT authentication và deployment beta trên Vercel/Render. Sản phẩm có workflow end-to-end, feedback tối thiểu và Founder Insights dạng aggregate.

Ở lớp ML, dự án đã đi xa hơn prototype thông thường về governance: dataset versioning, label QA, assembly, training contract, model registry, review gate, deployment decision, release audit và offline shadow review. Điểm còn thiếu quyết định không nằm ở pipeline, mà ở lượng dữ liệu beta thật đã được ẩn danh, review và gắn nhãn đáng tin cậy.
