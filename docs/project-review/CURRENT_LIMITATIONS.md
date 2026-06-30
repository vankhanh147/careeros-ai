# Giới hạn hiện tại

## Product validation

- Sản phẩm đã beta-ready về kỹ thuật nhưng chưa có bằng chứng đủ mạnh về retention, outcome nghề nghiệp hoặc product-market fit.
- Founder Insights là aggregate lifetime, chưa có cohort hoặc time-window analysis.
- Career Diagnosis chưa tồn tại như một module độc lập; giá trị diagnosis hiện được phân tán qua profile, matching, skill gap và roadmap.
- Chưa có frontend E2E automation; production smoke test vẫn là checklist thủ công.

## Matching và coaching

- Role/stack detection, evidence và criticality vẫn dựa trên dictionary/heuristic; title hoặc công nghệ ít phổ biến có thể bị phân loại sai.
- `pypdf` không đọc tốt scanned/image PDF; chưa có OCR. JD upload chưa hỗ trợ DOCX.
- Resume Feedback, Roadmap và Interview là template-based; chất lượng phụ thuộc vào text extraction và analysis đầu nguồn.
- Hệ thống không xác minh người dùng thật sự đã hoàn thành project hoặc sở hữu kỹ năng.
- Một phần analysis history được recompute theo logic hiện tại, nên insight cũ có thể thay đổi khi matcher thay đổi.

## Semantic và ML

- Semantic model được tắt mặc định trên Render Free để tránh startup timeout; khi tắt, hệ thống chỉ dùng rule-based signal.
- Training dataset v3 phụ thuộc gần như hoàn toàn vào 300 synthetic cases và 10 benchmark cases; approved beta count là 0.
- Benchmark U01–U10 quá nhỏ để đại diện toàn bộ thị trường tuyển dụng công nghệ.
- Metric từ synthetic split có thể lạc quan do template similarity và bias tạo dữ liệu.
- Chưa có model candidate vượt trọn governance pipeline; chưa có runtime shadow hoặc production ML inference.
- Chưa có continuous learning, active learning hay model monitoring từ production outcome.

## Data và governance

- Registry, audit, decision và review artifacts hiện là JSON/file-based; phù hợp MVP nhưng chưa có signed artifact, access-control chuyên biệt hoặc external immutable store.
- Human review workflow có contract nhưng chưa có quy trình vận hành với reviewer thật ở quy mô đáng kể.
- Không có nhãn outcome như callback, interview pass hoặc hired; vì vậy hệ thống chưa thể học trực tiếp “khả năng tuyển dụng”.

## Security và operations

- JWT lưu trong localStorage là lựa chọn MVP, chưa phải phương án tối ưu nhất cho security production.
- Chưa có Alembic; thay đổi schema production vẫn có thể cần migration thủ công.
- Logging chưa có request ID, structured JSON, Sentry hoặc observability đầy đủ.
- Render Free có cold start và giới hạn tài nguyên; semantic/torch không phù hợp để load mặc định.
- Local upload fallback không bền vững; production phải cấu hình Supabase Storage.

## Ranh giới kinh doanh

- Chưa có recruiter-facing product, payment, subscription hoặc doanh thu được kiểm chứng.
- Chưa có market-specific taxonomy theo từng công ty/quốc gia.
- Không nên hứa “đậu phỏng vấn”, “được tuyển” hoặc dùng match score như xác suất tuyển dụng.

## Hàm ý ưu tiên

Khoảng trống lớn nhất hiện không phải thiếu thêm feature. Đó là dữ liệu beta thật, quality review, đo outcome và kiểm chứng người dùng có quay lại learning loop hay không. Đầu tư ML production trước khi có các bằng chứng này sẽ tăng độ phức tạp nhanh hơn giá trị.
