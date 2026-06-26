# Dataset Promotion Workflow

## Mục tiêu

Dataset promotion giúp CareerOS AI tạo dataset version mới một cách có kiểm soát khi có thêm benchmark hoặc beta labels đã ẩn danh.

## Khi nào được promote dataset

Chỉ promote dataset khi:

- Source dataset metadata tồn tại.
- Target dataset version chưa tồn tại.
- Beta data nếu có đã được ẩn danh.
- Beta cases nếu dùng cho training/evaluation nghiêm túc đã có human review.
- Dataset mới có metadata riêng và không sửa im lặng dataset cũ.

## Config promotion

Config mẫu nằm tại:

```text
backend/ml/configs/dataset_promotion_config.json
```

Các field chính:

- `source_dataset_version`
- `target_dataset_version`
- `include_synthetic`
- `include_benchmark`
- `include_beta`
- `beta_source_path`
- `minimum_beta_cases`
- `require_human_review`
- `notes`

## Dry-run

Lệnh dry-run:

```bash
python scripts/promote_dataset_version.py --dry-run
```

Dry-run chỉ in kế hoạch promote và không tạo file mới.

## Write mode

Khi bỏ `--dry-run`, script sẽ tạo metadata target dạng draft:

- `status: draft`
- `production_safe: false`

Dataset draft không đồng nghĩa được dùng để train production model.

## Human review

Nếu `require_human_review=true`, mỗi beta case phải có metadata review như:

```json
{
  "human_review": {
    "reviewed": true,
    "reviewer": "internal",
    "notes": "Đã ẩn danh và kiểm tra label."
  }
}
```

## Ranh giới

- Không train model.
- Không đổi production scoring.
- Không đổi database schema.
- Không đổi API hoặc UI production.
- Không lưu PII.
