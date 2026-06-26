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
