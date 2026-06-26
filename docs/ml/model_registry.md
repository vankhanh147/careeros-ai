# Model Registry

## Mục tiêu

Model registry lưu metadata model artifact dưới dạng JSON để biết model được train từ dataset nào, dùng feature version nào và có metrics ra sao.

## Metadata chuẩn

Mỗi model registry record nên có:

- `model_name`
- `model_version`
- `dataset_version`
- `feature_version`
- `accuracy`
- `macro_f1`
- `created_at`
- `training_command`
- `artifact_paths`
- `production_safe`
- `notes`

## Ranh giới

Registry trong Phase 10.0 chỉ là file JSON local, chưa phải model serving system.

Model có trong registry không đồng nghĩa được dùng làm production score. Mọi quyết định production phải qua benchmark, beta validation và review riêng.
