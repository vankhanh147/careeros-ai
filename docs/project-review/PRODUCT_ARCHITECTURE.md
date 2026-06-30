# Kiến trúc sản phẩm

## Hành trình giá trị

```text
Đăng ký / Đăng nhập
        ↓
Hồ sơ nghề nghiệp
        ↓
CV + Job Description
        ↓
Resume ↔ JD Matching
        ↓
Skill Gap + Resume Feedback
        ↓
Roadmap học tập
        ↓
Mock Interview
        ↓
Hoàn thành mục học tập → cập nhật CV → phân tích lại
```

Luồng này là xương sống của sản phẩm. Mỗi bước tạo đầu vào cho bước kế tiếp, nhờ đó CareerOS AI không trở thành tập hợp các trang rời rạc.

## Các lớp sản phẩm

### 1. Lớp hồ sơ và dữ liệu nghề nghiệp

Career Profile lưu mục tiêu, trình độ, kỹ năng, kinh nghiệm và timeline. Documents quản lý CV và JD trong phạm vi từng tài khoản. Đây là dữ liệu nền để mọi insight sau đó có ngữ cảnh cá nhân.

### 2. Lớp career intelligence

Matching đánh giá độ phù hợp giữa CV và JD. Skill Gap phân loại khoảng trống theo ưu tiên. Resume Feedback biến phân tích thành các chỉnh sửa CV an toàn, luôn phân biệt giữa bằng chứng đã có và kỹ năng chỉ nên bổ sung nếu người dùng thực sự đã làm.

### 3. Lớp phát triển năng lực

Roadmap V2 chuyển khoảng trống thành focus, bài thực hành, minh chứng có thể thêm vào CV, chuẩn bị phỏng vấn và kết quả mong đợi. Mock Interview V2 chọn câu hỏi theo role/stack, missing skills và ngữ cảnh roadmap, sau đó chấm theo keyword với feedback giải thích được.

### 4. Lớp learning loop

Tiến độ roadmap được giữ ở mức Lite. Dashboard dùng trạng thái hồ sơ, tài liệu, analysis, roadmap, interview và thời điểm CV mới để đề xuất hành động tiếp theo. Hệ thống không tự chạy lại phân tích và không biến thành task manager.

### 5. Lớp product signal

Usage events và feedback hữu ích/chưa hữu ích cung cấp tín hiệu beta tối thiểu. Founder Insights tổng hợp funnel, feedback, missing skills, matching health và learning-loop signal mà không lộ email, CV hoặc JD.

## Kiến trúc kỹ thuật cấp cao

```text
Next.js / React / TypeScript
            ↓ REST API + JWT
FastAPI modular monolith
    ├── Product services
    ├── AI services
    └── Offline ML workspace
            ↓
PostgreSQL / Supabase
Supabase Storage (private)
```

Kiến trúc modular monolith phù hợp với giai đoạn hiện tại: deployment đơn giản, ownership rõ, chi phí vận hành thấp và chưa có tải thật để biện minh cho microservices.

## Nguyên tắc trải nghiệm

- Tiếng Việt là ngôn ngữ mặc định.
- CTA phải trả lời được “tôi nên làm gì tiếp theo?”.
- Empty, loading và error state là một phần của workflow, không phải chi tiết trang trí.
- Nội dung dài phải wrap, responsive và không tạo horizontal scroll.
- Điểm thử nghiệm không được nổi hơn điểm production hoặc gây hiểu nhầm.

## Ranh giới sản phẩm

CareerOS AI đưa ra coaching signal, không cam kết tuyển dụng và không xác minh người dùng thực sự sở hữu kỹ năng. Sản phẩm không tự bịa metric, project hoặc thành tích. Dữ liệu nghề nghiệp được giới hạn theo quyền sở hữu của người dùng; private storage và aggregate founder metrics giúp giảm rủi ro lộ PII.
