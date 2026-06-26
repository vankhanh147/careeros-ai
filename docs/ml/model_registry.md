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

## Registry draft từ Training Job Contract

Từ Phase 10.4, `run_training_job.py` có thể tạo registry draft tại:

- `backend/ml/registry/{model_version}.json`

Registry draft phải có:

- `dataset_hash`
- `artifact_paths`
- `status=draft`
- `production_safe=false`

Nếu `model_version` đã tồn tại, training job phải fail và không overwrite artifact cũ.
