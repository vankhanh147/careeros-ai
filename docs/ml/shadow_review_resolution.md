# Shadow Review Resolution Export

## Mục tiêu

Resolution Export chuyển các shadow queue items đã được reviewer xử lý sang Label Review Draft. Đây là bước bàn giao metadata an toàn, không phải training approval.

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

## Điều kiện export

Chỉ item có `review_status=promoted_to_label_review` được export. Item phải có:

- Reviewer.
- Resolution notes.
- Resolved label hợp lệ.
- Review time.
- Label confidence trong `0..1`.
- `anonymized=true`.
- `approved_for_label_review=true`.
- `approved_for_training=false`.
- `stored_raw_text=false`.

## Mapping sang Label Review Pipeline

Output chứa:

- `exported_items`: metadata resolution và traceability từ shadow queue.
- `cases`: Label Review Draft tương thích `label_review_schema.md`.

Mỗi draft bắt đầu với:

```text
previous_status=ANONYMIZED
review_status=UNDER_REVIEW
approved_for_training=false
```

Export không tạo status `APPROVED`, `PROMOTED` hoặc `TRAINABLE`.

## Human review boundary

Reviewer trong shadow queue xác nhận case đủ điều kiện bàn giao, nhưng Label Review Pipeline vẫn phải review label confidence, disagreement reason, anonymization và training suitability.

Chỉ Label Review QA và Dataset Promotion mới có thể đưa case vào training dataset.

## Privacy boundary

- Không export raw CV/JD text.
- Không chứa email hoặc số điện thoại.
- `stored_raw_text=false` ở export, exported item và label review draft.
- PII/mojibake khiến export bị từ chối.

## CLI

Dry-run:

```bash
python scripts/export_shadow_review_resolutions.py --dry-run
```

Write mode:

```bash
python scripts/export_shadow_review_resolutions.py
```

Input:

```text
backend/ml/reviews/shadow_review_queue.json
```

Output:

```text
backend/ml/reviews/shadow_label_review_draft.json
```

Nếu chưa có queue, CLI trả `no_queue`, recommendation `build shadow review queue first`, không crash và không ghi output.
