# Experiment Tracking

## Mục tiêu

Experiment tracking giúp ghi lại thử nghiệm training/evaluation một cách nhẹ, không cần MLflow hoặc hạ tầng lớn.

## Metadata chuẩn

Mỗi experiment nên có:

- `experiment_id`
- `model`
- `dataset`
- `metrics`
- `notes`
- `status`

## Status gợi ý

- `draft`
- `running`
- `completed`
- `review_needed`
- `rejected`

## Quy tắc

- Experiment không được tự động deploy model.
- Experiment phải ghi rõ dataset version và model version.
- Nếu metrics cao bất thường trên synthetic data, phải ghi chú nguy cơ leakage hoặc overfitting.
- Real beta labels phải được ẩn danh trước khi dùng cho experiment.

## Experiment record từ Training Job Contract

Từ Phase 10.4, mỗi training job thật phải ghi experiment record trong `backend/ml/experiments/`.

Record tối thiểu gồm:

- `run_id`
- `dataset_version`
- `dataset_hash`
- `feature_version`
- `model_name`
- `model_version`
- `training_started_at`
- `training_finished_at`
- `metrics`
- `artifact_paths`
- `status`
- `production_safe=false`

Dry-run không ghi experiment record.

## Liên kết với Model Review Gate

Từ Phase 10.5, experiment record là bằng chứng bắt buộc của registry review. Gate kiểm tra `model_version` và `dataset_hash` trong experiment phải khớp registry. Thiếu experiment hoặc metadata không khớp sẽ là FAIL.

## Liên kết với Deployment Decision

Evaluation report và experiment evidence của candidate là input cho model comparison. Deployment Decision Record chỉ tham chiếu bằng chứng đã có; không chạy training hoặc inference mới.
