# Phase 11.2 - Shadow Disagreement Review Queue

Date: 2026-06-28

## Mục tiêu

Phase 11.2 tạo review queue offline để triage disagreement records từ shadow harness trước human review và Label Review Pipeline.

## Workflow

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

## Thành phần

- `backend/ml/configs/shadow_review_queue_schema.json`
- `backend/app/ml/shadow_review_queue.py`
- `backend/scripts/build_shadow_review_queue.py`
- `backend/tests/test_shadow_review_queue.py`
- `docs/ml/shadow_review_queue.md`

## Schema

Queue lưu source report, item counts và items. Mỗi item có expected/rule/candidate/hybrid labels, disagreement type, severity, review reason, recommended action và review state.

Mọi item giữ:

- `stored_raw_text=false`
- `approved_for_training=false`
- `approved_for_label_review=false` cho tới khi human review hoàn tất

## No-source behavior

Nếu chưa có `shadow_summary.json`, CLI trả queue status `no_source_report`, recommendation `run shadow harness write mode first`, không crash và không ghi output.

## Validation

Validator chặn:

- Queue/item ID rỗng hoặc trùng.
- Case ID rỗng.
- Severity, disagreement type hoặc review status không hợp lệ.
- Raw text storage.
- `approved_for_training` khác false.
- Thiếu reviewer ở trạng thái review.
- PII hoặc mojibake.

## Safety boundary

- Queue chỉ là review signal.
- Không runtime shadow hoặc production inference.
- Không dùng disagreement trực tiếp làm training label.
- Không thay production scoring, API, UI hoặc database schema.

## Giới hạn

- Repository chưa có shadow summary thật vì harness mới chạy dry-run.
- Chưa có candidate thật nên chưa có disagreement records thực tế.
- Human review vẫn thực hiện qua JSON offline, chưa có UI.
- Severity dùng deterministic rules đơn giản.

## Recommendation Phase 11.3

Phase 11.3 chỉ nên chuẩn hóa offline review resolution/export sang Label Review Pipeline, kèm reviewer traceability. Chưa tích hợp production runtime.
