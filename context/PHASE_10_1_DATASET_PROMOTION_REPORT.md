# Phase 10.1 - Dataset Promotion Workflow

Date: 2026-06-26

## Mục tiêu

Phase 10.1 thêm workflow promote dataset có kiểm soát để CareerOS AI có thể tạo dataset version mới khi có beta labels đã ẩn danh. Phase này không train model và không thay đổi production scoring.

## Workflow đã thêm

- Tạo config mẫu `backend/ml/configs/dataset_promotion_config.json`.
- Tạo script `backend/scripts/promote_dataset_version.py`.
- Mở rộng `backend/app/ml/training_infra.py` với parser/validator cho promotion config.
- Tạo tài liệu `docs/ml/dataset_promotion.md`.

## Dry-run behavior

Lệnh:

```bash
python scripts/promote_dataset_version.py --dry-run
```

Dry-run sẽ:

- Đọc promotion config.
- Validate source dataset metadata.
- Validate target version chưa tồn tại.
- Validate beta source nếu `include_beta=true`.
- In kế hoạch promote.
- Không tạo file metadata mới.

## Write mode

Khi bỏ `--dry-run`, script sẽ tạo metadata target như:

- `backend/ml/datasets/dataset_v3_metadata.json`
- `status: draft`
- `production_safe: false`

Script không overwrite dataset version cũ.

## Validation rules

- `target_dataset_version` không được trùng `source_dataset_version`.
- Source dataset metadata phải tồn tại.
- Target dataset metadata chưa được tồn tại.
- Nếu `include_beta=true`, `beta_source_path` phải tồn tại.
- Nếu `require_human_review=true`, mỗi beta case phải có review metadata với `reviewed=true`.
- Beta source không được có PII rõ ràng như email hoặc số điện thoại.
- Beta source không được có dấu hiệu mojibake.
- Dataset metadata mới phải đủ field bắt buộc.

## Giới hạn

- Chưa merge dữ liệu vật lý thành một dataset artifact mới.
- Chưa có real beta labels trong repo.
- Chưa có model training hoặc evaluation tự động sau promotion.
- Chưa có approval workflow nhiều người.

## Recommendation Phase 10.2

Phase 10.2 nên tập trung vào beta label schema nâng cao và anonymization checklist để real beta data có thể đi vào dataset promotion mà vẫn an toàn.
