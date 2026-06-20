# Phase 8.5 - Real Beta Dataset Foundation

Date: 2026-06-21

## Mục tiêu

Phase 8.5 tạo nền tảng dữ liệu cho AI thật trong tương lai mà không thay đổi scoring production, `match_score`, `final_score`, database schema, UI lớn hoặc API contract cũ.

Phase này chưa train model, chưa dùng LLM API, chưa fine-tuning và chưa thêm vector database.

## Dataset philosophy

CareerOS AI cần dữ liệu tốt trước khi nghĩ đến model trainable. Dữ liệu phải giúp trả lời:

- Matcher đúng ở đâu?
- Matcher over-score hoặc under-score ở đâu?
- User có đồng ý với phân tích không?
- Case nào cần human review trước khi dùng làm training label?

Nguyên tắc chính:

- Ưu tiên dữ liệu đã ẩn danh.
- Không lưu email, raw CV text hoặc raw JD text vào dataset docs.
- Feedback đơn lẻ không đủ để đổi scoring.
- Dataset dùng để review pattern, không dùng để kết luận tuyệt đối về năng lực ứng viên.

## Benchmark dataset và beta dataset

### Benchmark dataset

Benchmark dataset là bộ case cố định để chống regression khi thay matcher.

Nguồn hiện tại:

- `docs/benchmark-v1/`

Benchmark U01-U10 vẫn là guardrail chính cho Matching V2.1, semantic foundation và hybrid evaluation.

### Beta dataset

Beta dataset là nơi ghi lại case thật đã ẩn danh từ user beta.

Đã tạo:

- `docs/datasets/README.md`
- `docs/datasets/beta/README.md`
- `docs/datasets/beta/U011.json`
- `docs/datasets/beta/U012.json`
- `docs/datasets/beta/U013.json`
- `docs/datasets/feedback_label_schema.json`

Các file U011-U013 hiện là template pending real case, chưa chứa dữ liệu người dùng thật.

## Labeling strategy

Feedback label tối thiểu gồm:

- `case_id`
- `user_agreed`
- `user_disagreed`
- `reason`
- `expected_score_range`
- `reviewer_notes`

Mapping hiện tại:

- `useful=true` được xem là agreed label.
- `useful=false` được xem là disagreed label.

Đây chỉ là nhãn thô. Trước khi dùng cho training thật, cần human review để xác nhận lý do disagreement.

## Dataset export layer

Đã thêm:

- `backend/app/ai/dataset_export.py`

Helper hiện hỗ trợ:

- build benchmark case payload.
- build feedback label payload từ `UserFeedback`.
- build analysis summary từ `MatchAnalysis`.
- export JSON UTF-8 bằng `write_dataset_json`.

Export summary cố tình không chứa:

- CV text đầy đủ.
- JD text đầy đủ.
- email hoặc thông tin nhận dạng user.

## Founder insights support

Đã thêm metadata aggregate nhỏ vào founder insights:

- `feedback_labels.total_feedback_labels`
- `feedback_labels.agreed_labels`
- `feedback_labels.disagreed_labels`

Đây là field additive trong `GET /api/founder/insights`, không phá client cũ và không hiển thị PII.

## Future training path

Đường đi an toàn trước Phase 9.0:

1. Thu thập beta cases đã ẩn danh vào `docs/datasets/beta/`.
2. Gắn feedback label useful/not useful và lý do ngắn.
3. Human review các case disagreement.
4. So sánh với benchmark U01-U10.
5. Chỉ khi có đủ pattern lặp lại mới thiết kế Trainable Matching Model.

## Giới hạn hiện tại

- Chưa có raw anonymized CV/JD artifacts.
- Chưa có training pipeline.
- Chưa có export command tự động từ production database.
- Label useful/not useful còn thô, chưa đủ cho supervised learning trực tiếp.
- Dataset template trong repo chưa đại diện cho dữ liệu beta thật.

## Recommendation

Phase tiếp theo nên ưu tiên thu thập real anonymized beta cases và review disagreement trước khi train model. Không nên chuyển sang trainable matching nếu chưa có tối thiểu một tập case thật đủ đa dạng và có human label rõ ràng.