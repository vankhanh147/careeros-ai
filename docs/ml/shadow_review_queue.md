# Shadow Disagreement Review Queue

## Mục tiêu

Shadow Review Queue gom các comparison records cần human review từ Offline Shadow Evaluation Harness. Queue là công cụ triage nội bộ, không phải training dataset và không chạy trong production.

```text
Shadow Summary
↓
Review Required Records
↓
Shadow Review Queue
↓
Human Review
↓
Label Review Pipeline
↓
Dataset Promotion
```

## Nguồn dữ liệu

Input mặc định:

```text
backend/ml/reports/shadow_summary.json
```

Queue builder chỉ lấy records có `review_required=true`. Comparison metadata được giữ lại, nhưng raw CV/JD text không được lưu.

## Disagreement types

- `rule_vs_candidate`
- `rule_vs_expected`
- `candidate_vs_expected`
- `low_confidence`
- `benchmark_anomaly`
- `no_candidate`

## Severity

- `high`: benchmark anomaly hoặc label lệch từ hai bậc trở lên.
- `medium`: confidence thấp, thiếu candidate hoặc disagreement một bậc.
- `low`: disagreement nhẹ còn lại.

High severity được review trước. Severity không phải training weight và không tự thay đổi label.

## Human review flow

Review status:

```text
pending
↓
under_review
↓
resolved hoặc rejected
↓
promoted_to_label_review
```

`promoted_to_label_review` chỉ chuyển case sang Label Review Pipeline. Nó không có nghĩa `approved_for_training=true`.

Reviewer cần:

1. Kiểm tra expected/rule/candidate/hybrid labels.
2. Xem lại role, stack và evidence trong nguồn đã ẩn danh.
3. Ghi notes và quyết định có bàn giao sang label review không.
4. Nếu bàn giao, tạo label review metadata theo `label_review_schema.md`.
5. Chỉ dataset promotion mới được sử dụng label đã approved.

## Validation

Queue validator kiểm tra:

- Queue ID và case ID không rỗng.
- Item ID duy nhất.
- Severity, disagreement type và review status hợp lệ.
- Reviewer bắt buộc từ `under_review` trở đi.
- `stored_raw_text=false`.
- `approved_for_training=false`.
- Không PII.
- Không mojibake.

## CLI

Dry-run:

```bash
python scripts/build_shadow_review_queue.py --dry-run
```

Write mode:

```bash
python scripts/build_shadow_review_queue.py
```

Output:

```text
backend/ml/reviews/shadow_review_queue.json
```

Nếu chưa có shadow summary, CLI trả `no_source_report`, không crash và không ghi queue.

## Safety boundary

- Disagreement chỉ là review signal.
- Không dùng queue trực tiếp làm training label.
- Không lưu raw text.
- Không thay production score, API hoặc UI.
