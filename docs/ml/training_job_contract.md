# Training Job Contract

## Mục tiêu

Training Job Contract chuẩn hóa cách CareerOS AI train model offline từ Phase 10.4 trở đi. Mọi training script mới phải đi qua contract này để đảm bảo dataset, config, experiment, registry và report có thể truy vết được.

Contract này không thay production scoring, không thay `match_score`, không thay `final_score`, không đổi database schema và không tích hợp runtime inference mới.

## Input bắt buộc

Training job chỉ được đọc từ dataset artifact đã assembly:

- `backend/ml/datasets/training_dataset_v3.json`
- `backend/ml/datasets/training_dataset_manifest.json`
- `backend/ml/configs/training_config.json`

Training job không được đọc trực tiếp từ:

- `docs/datasets/synthetic/synthetic_cases.json`
- `docs/benchmark-v1/*`
- beta raw files
- beta review files chưa assembly

## Training config

Config tối thiểu phải có:

- `dataset_version`
- `feature_version`
- `classifier`
- `model_name`
- `model_version`
- `random_seed`
- `split_ratio`

Nếu thiếu field bắt buộc, training job phải fail trước khi train.

## Validation bắt buộc

Training job phải fail nếu:

- Dataset artifact không tồn tại.
- Manifest không tồn tại.
- `artifact_hash` trong manifest không khớp SHA256 của artifact.
- `dataset_version` không khớp giữa config, artifact và manifest.
- Dataset rỗng hoặc thiếu `cases`.
- Label không thuộc `good`, `medium`, `weak`, `mismatch`.
- `model_version` đã tồn tại trong registry hoặc artifact directory.
- Có dấu hiệu PII, mojibake hoặc file không phải UTF-8 chuẩn.
- Config thiếu field bắt buộc.

## Output khi chạy thật

Training job ghi các output sau:

- Model artifacts trong `backend/ml/models/{model_version}/`.
- Experiment record trong `backend/ml/experiments/`.
- Registry draft trong `backend/ml/registry/`.
- Evaluation report trong `backend/ml/reports/`.

Registry draft luôn có:

- `production_safe=false`
- `status=draft`

Registry draft không đồng nghĩa model được dùng trong production.

## Training job metadata

Mỗi run phải có:

- `run_id`
- `dataset_version`
- `dataset_hash`
- `feature_version`
- `model_name`
- `model_version`
- `classifier`
- `training_started_at`
- `training_finished_at`
- `metrics`
- `artifact_paths`
- `status`
- `production_safe=false`

## Exit code rules

- Exit code `0`: contract hợp lệ và job hoàn tất hoặc dry-run hợp lệ.
- Exit code `1`: validation fail, config lỗi, hash mismatch, duplicate model version hoặc training lỗi.

## Dry-run

Lệnh:

```bash
python scripts/run_training_job.py --dry-run
```

Dry-run chỉ validate contract và in kế hoạch. Dry-run không ghi model artifact, experiment, registry hoặc evaluation report.

## Production boundary

Training job là offline pipeline. Kể cả khi metrics tốt, model vẫn chưa được phép thay production score nếu chưa qua benchmark, beta validation, review registry và deployment decision riêng.
