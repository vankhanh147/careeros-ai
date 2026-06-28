# Phase 11.3 - Shadow Review Resolution Export

Date: 2026-06-28

## Mục tiêu

Phase 11.3 tạo pipeline offline để export shadow review items đã xử lý sang Label Review Draft an toàn. Export không tự động approve training labels.

## Workflow

```text
Shadow Review Queue
↓
Resolved Items
↓
Resolution Export
↓
Label Review Draft
↓
Label Review Pipeline
↓
Dataset Promotion
```

## Thành phần

- `backend/ml/configs/shadow_review_resolution_schema.json`
- `backend/app/ml/shadow_review_resolution.py`
- `backend/scripts/export_shadow_review_resolutions.py`
- `backend/tests/test_shadow_review_resolution.py`
- `docs/ml/shadow_review_resolution.md`

## Schema

Export lưu source queue, exported resolution items và `cases` tương thích Label Review Pipeline. Draft bắt đầu ở `UNDER_REVIEW`, có `previous_status=ANONYMIZED` và `approved_for_training=false`.

## No-queue behavior

Nếu chưa có `shadow_review_queue.json`, CLI trả `no_queue`, recommendation `build shadow review queue first`, không crash và không ghi draft.

## Validation

Validator yêu cầu reviewer, notes, review time, resolved label, confidence `0..1`, anonymization và label-review approval. Validator chặn duplicate case ID, raw text, PII, mojibake và mọi `approved_for_training=true`.

## Safety boundary

- Chỉ export item `promoted_to_label_review`.
- Không export raw CV/JD text.
- Không tạo training label.
- Không đổi production scoring, API, UI hoặc database schema.
- Không runtime shadow hoặc production inference.

## Giới hạn

- Repository chưa có shadow queue thật.
- Chưa có resolved items từ reviewer thật.
- Review/export vẫn dùng JSON offline, chưa có UI.
- Dataset version của draft dùng `shadow_review_draft` nếu queue chưa cung cấp version.

## Recommendation Phase 11.4

Phase 11.4 nên nối Label Review Draft vào QA validator hiện có theo dry-run, kiểm tra transition/anonymization và chuẩn bị dataset promotion plan. Chưa tự động promote hoặc train.
