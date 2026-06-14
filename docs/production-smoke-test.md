# CareerOS AI Production Smoke Test

Checklist này dùng sau mỗi lần deploy Render backend và Vercel frontend để xác nhận MVP production vẫn chạy ổn.

## Production URLs

- Frontend: `https://careeros-ai-bay.vercel.app`
- Backend: `https://careeros-ai-backend.onrender.com`
- Health check: `https://careeros-ai-backend.onrender.com/health`

## Trước Khi Test

- Render backend đã deploy thành công.
- Vercel frontend đã deploy thành công.
- `NEXT_PUBLIC_API_URL=https://careeros-ai-backend.onrender.com` trên Vercel.
- `BACKEND_CORS_ORIGINS=https://careeros-ai-bay.vercel.app,http://localhost:3000` trên Render.
- Supabase PostgreSQL `DATABASE_URL` hợp lệ.
- Supabase Storage private bucket `career-documents` đã tồn tại.
- Render env có `SENTENCE_TRANSFORMERS_ENABLED=false` nếu dùng Render Free.

## 1. Health Check

- Mở `https://careeros-ai-backend.onrender.com/health`.
- Kỳ vọng response:

```json
{"status":"ok","service":"career-os-ai-api"}
```

## 2. Register / Login

- Mở frontend production.
- Tạo user mới bằng email test.
- Đăng xuất nếu cần.
- Đăng nhập lại bằng email/password vừa tạo.
- Kỳ vọng: login thành công và redirect vào `/dashboard`.

## 3. Profile

- Vào `/profile`.
- Nhập hoặc cập nhật `target role`, `current level`, `skills`, `experience summary`, `projects summary`, `career goal`, `timeline`.
- Bấm lưu.
- Reload trang.
- Kỳ vọng: dữ liệu vẫn hiển thị đúng.

## 4. Upload CV / JD

- Vào `/documents`.
- Upload một file CV PDF nhỏ hơn 5MB.
- Kỳ vọng: CV xuất hiện trong danh sách.
- Paste một JD với title, company, content và source URL.
- Kỳ vọng: JD xuất hiện trong danh sách.
- Upload thêm một JD file `.pdf` hoặc `.txt`.
- Kỳ vọng: JD upload xuất hiện và content được đọc.

## 5. Supabase Storage Upload / Delete

- Sau khi upload CV/JD, mở Supabase Storage bucket `career-documents`.
- Kiểm tra object được tạo theo path:

```text
users/{user_id}/resumes/{uuid}-{filename}
users/{user_id}/job-descriptions/{uuid}-{filename}
```

- Xóa CV/JD từ UI.
- Kỳ vọng item biến mất khỏi UI và object tương ứng bị xóa khỏi Supabase Storage.

## 6. Analysis

- Vào `/analysis`.
- Chọn một CV và một JD đã lưu.
- Bấm phân tích CV ↔ JD.
- Kỳ vọng hiển thị điểm phù hợp, kỹ năng đã khớp, kỹ năng còn thiếu, keyword overlap, scoring breakdown, CV/JD text preview, skill gap summary và improvement plan.

Lưu ý: trên Render Free, `semantic_score` có thể là `0` vì `SENTENCE_TRANSFORMERS_ENABLED=false`; đây là fallback chủ đích.

## 7. Roadmap

- Vào `/roadmap`.
- Chọn analysis gần đây nếu có.
- Nhập timeline, ví dụ `1 tuần` hoặc `1 tháng`.
- Bấm tạo roadmap.
- Kỳ vọng roadmap được tạo thành công, số step khớp timeline, từng step có focus, skills, actions và expected output.

## 8. Mock Interview

- Vào `/interview`.
- Chọn analysis gần đây nếu có.
- Nhập target role nếu muốn.
- Bấm bắt đầu phỏng vấn.
- Trả lời ít nhất một câu.
- Kỳ vọng nhận score và feedback sau câu trả lời.
- Bấm hoàn thành.
- Kỳ vọng session chuyển sang finished và có điểm tổng kết.

## 9. Dashboard

- Vào `/dashboard`.
- Kỳ vọng hiển thị trạng thái hồ sơ nghề nghiệp, số CV/JD, phân tích gần nhất, roadmap gần nhất, phiên phỏng vấn gần nhất và checklist bước tiếp theo.
- Với user mới, dashboard phải hiển thị next actions phù hợp thay vì lỗi.

## 10. Delete CV / JD

- Vào `/documents`.
- Xóa một CV.
- Xóa một JD.
- Kỳ vọng UI refresh đúng, item không còn trong danh sách, không lỗi 500, object Supabase Storage bị xóa nếu item có file upload.

## Smoke Test Result Template

```text
Date:
Tester:
Backend deploy:
Frontend deploy:

Health check:
Register/Login:
Profile:
Upload CV/JD:
Supabase Storage upload/delete:
Analysis:
Roadmap:
Mock Interview:
Dashboard:
Delete CV/JD:

Issues found:
Next actions:
```
