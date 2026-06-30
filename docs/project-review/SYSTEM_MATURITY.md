# Đánh giá mức trưởng thành hệ thống

## Thang đánh giá

- **Foundation:** đã có cấu trúc và contract, chưa chứng minh qua vận hành thực.
- **MVP Operational:** hoạt động end-to-end cho beta, còn giới hạn production.
- **Evaluation Ready:** có dữ liệu, metrics và safety gate để đánh giá có kiểm soát.
- **Evidence Needed:** kỹ thuật đã sẵn sàng hơn bằng chứng người dùng.

## Ma trận trưởng thành

| Năng lực | Mức hiện tại | Điểm mạnh | Khoảng trống quyết định |
| --- | --- | --- | --- |
| Product workflow | MVP Operational | Luồng profile → matching → roadmap → interview → rerun khép kín | Cần retention và outcome beta thật |
| UX | MVP Operational | Tiếng Việt, responsive, CTA/empty/loading/error states | Chưa có frontend E2E automation |
| Matching AI | MVP Operational | Explainable, deterministic, calibrated bằng benchmark | Heuristic, phụ thuộc extraction và dictionary |
| Coaching AI | MVP Operational | Resume Feedback, Roadmap V2, Interview V2 có action rõ | Template-based, chưa xác minh completion |
| Taxonomy | Evaluation Ready | Role/stack/alias foundation dùng chung | Static, chưa có market-specific validation |
| Semantic | Foundation | Optional, lazy-load, fallback an toàn | Tắt mặc định trên Render Free |
| Trainable ML | Evaluation Ready | Prototype, feature engineering và ablation đã có | Synthetic-heavy, chưa có approved beta labels |
| Dataset | Evidence Needed | 310-case artifact, manifest, statistics, fingerprint | 0 beta case trong training dataset |
| ML governance | Evaluation Ready | Registry, review, decision, audit, shadow review workflow | File-based, chưa vận hành với candidate thật |
| Privacy | Foundation tốt | Không raw text trong shadow, anonymization gate | Cần quy trình consent và reviewer vận hành thật |
| Deployment | MVP Operational | Vercel, Render, Supabase, private storage | Free-tier constraints, monitoring cơ bản |
| Observability | Foundation | Logging và error handling cơ bản | Chưa có request tracing, Sentry, metrics chuẩn |
| Database operations | Foundation | PostgreSQL/Supabase hoạt động | Chưa có Alembic migration system |
| Startup validation | Evidence Needed | Founder metrics và feedback foundation | Chưa có PMF, revenue hoặc cohort evidence |

## Nhận định tổng thể

CareerOS AI đã vượt giai đoạn demo: sản phẩm có workflow thật, deployment thật và logic AI có thể giải thích. Ở nhiều khía cạnh, governance ML đã trưởng thành hơn lượng dữ liệu mà nó đang quản lý. Đây vừa là lợi thế vừa là cảnh báo.

Lợi thế là hệ thống đã có ranh giới an toàn trước khi thử production ML. Cảnh báo là đầu tư thêm pipeline có thể tạo cảm giác tiến bộ trong khi rủi ro lớn nhất vẫn là thiếu beta evidence.

## Mức sẵn sàng

- **Sẵn sàng cho beta có kiểm soát:** Có.
- **Sẵn sàng thu nhãn beta đã ẩn danh:** Có, nếu bổ sung consent và reviewer operation.
- **Sẵn sàng train prototype offline:** Có.
- **Sẵn sàng đưa ML thành điểm production:** Chưa.
- **Sẵn sàng mở rộng hạ tầng phân tán:** Chưa cần.

## Tiêu chí trưởng thành tiếp theo

Hệ thống chỉ nên được coi là bước sang mức tiếp theo khi có:

1. Beta cases thật đã qua label QA.
2. Candidate vượt benchmark và beta holdout.
3. Offline shadow disagreement được human review.
4. Runtime cost/privacy/latency được đo.
5. Deployment decision riêng cho production, không suy ra từ training success.
