# Phase 10.2 - Label Review & Quality Assurance Pipeline

Date: 2026-06-26

## Mục tiêu

Phase 10.2 tạo pipeline review label và QA cho dữ liệu AI Training của CareerOS AI. Đây không phải phase train model và không thay đổi bất kỳ hành vi production nào.

## Workflow đã thêm

CareerOS AI hiện có workflow label review chuẩn:

```text
Dataset
↓
Label Review
↓
Quality Assurance
↓
Dataset Promotion
↓
Training
↓
Evaluation
↓
Model Registry
↓
Deployment Decision
```

Review status chuẩn:

```text
NEW → ANONYMIZED → UNDER_REVIEW → APPROVED → PROMOTED → TRAINABLE
```

## Metadata schema

Đã thêm:

- `docs/ml/label_review_schema.md`
- `backend/ml/configs/label_review_schema.json`

Mỗi review case cần có:

- `case_id`
- `dataset_version`
- `review_status`
- `reviewer`
- `review_time`
- `label_confidence`
- `disagreement_reason`
- `notes`
- `approved_for_training`
- `anonymized`

## Validator

Đã mở rộng `backend/app/ml/training_infra.py` với:

- `parse_label_review_schema`
- `load_label_review_cases`
- `validate_label_review_case`
- `validate_label_review_cases`
- `validate_label_review_file`

Validator kiểm tra:

- Metadata đủ field bắt buộc.
- `review_status` hợp lệ.
- Transition trạng thái hợp lệ.
- `approved_for_training=true` chỉ hợp lệ với `APPROVED`, `PROMOTED` hoặc `TRAINABLE`.
- `anonymized=true` là bắt buộc trước khi approved.
- `label_confidence` nằm trong khoảng `0..1`.
- Không có PII rõ ràng.
- Không có mojibake.

## QA script

Đã thêm:

- `backend/scripts/validate_label_review_pipeline.py`

Script in ra:

- Errors
- Warnings
- Ready for promotion
- Not ready

Script chỉ đọc review metadata offline và không ghi file mới.

## Sample review dataset

Đã thêm:

- `backend/ml/reviews/sample_review_cases.json`

File này chỉ là template giả lập, không chứa dữ liệu thật hoặc PII.

## Tài liệu

Đã thêm/cập nhật:

- `docs/ml/label_review_schema.md`
- `docs/ml/label_quality.md`
- `docs/ml/README.md`

## Giới hạn

- Chưa có real beta labels trong repo.
- QA pipeline hiện validate metadata JSON local, chưa có UI review hoặc multi-reviewer approval.
- Chưa merge review labels vào dataset artifact vật lý.
- Chưa có automated promotion gate nối trực tiếp với training script.

## Recommendation Phase 10.3

Phase 10.3 nên tập trung vào dataset assembly/export: gom synthetic, benchmark và approved beta review labels thành một dataset artifact versioned rõ ràng, vẫn giữ production scoring không đổi.