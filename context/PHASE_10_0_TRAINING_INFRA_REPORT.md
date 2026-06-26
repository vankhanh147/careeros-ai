# Phase 10.0 - AI Training Infrastructure Foundation

Date: 2026-06-26

## Mục tiêu

Phase 10.0 mở đầu CareerOS AI V2 bằng cách tạo nền tảng AI Training Infrastructure. Đây không phải phase cải thiện matcher và không thay đổi bất kỳ hành vi production nào.

## Đã thêm

### ML workspace

Tạo `backend/ml/` với các thư mục:

- `configs/`
- `datasets/`
- `experiments/`
- `models/`
- `registry/`
- `reports/`

Workspace này chỉ phục vụ training/evaluation metadata offline. Production code vẫn nằm trong `backend/app/`.

### Dataset versioning

Tạo metadata:

- `backend/ml/datasets/dataset_v2_metadata.json`

Metadata chuẩn gồm:

- `dataset_id`
- `version`
- `created_at`
- `source`
- `total_cases`
- `synthetic_cases`
- `benchmark_cases`
- `beta_cases`
- `notes`

### Model registry

Tạo registry records:

- `backend/ml/registry/matching_model_v1.json`
- `backend/ml/registry/hybrid_matching_model_v1.json`

Registry lưu `model_name`, `model_version`, `dataset_version`, `feature_version`, metrics, artifact paths và training command.

### Experiment tracking

Tạo template:

- `backend/ml/experiments/experiment_template.json`

Template đủ các field: `experiment_id`, `model`, `dataset`, `metrics`, `notes`, `status`.

### Evaluation report format

Tạo template:

- `backend/ml/reports/evaluation_report_template.json`

Template chuẩn hóa `accuracy`, `macro_f1`, `precision`, `recall`, `confusion_matrix`, `error_analysis`, `dataset_version` và `model_version`.

### Config foundation

Tạo config:

- `backend/ml/configs/training_config.json`

Config gồm random seed, split ratio, feature version, classifier và dataset version.

### Parser/validator

Tạo:

- `backend/app/ml/training_infra.py`

Module này chỉ parse/validate metadata JSON. Không train model, không inference và không thay production scoring.

### Documentation

Tạo:

- `docs/ml/README.md`
- `docs/ml/model_registry.md`
- `docs/ml/dataset_versioning.md`
- `docs/ml/experiment_tracking.md`

## Không thay đổi

- Không thay production scoring.
- Không thay `match_score`.
- Không thay `final_score`.
- Không đổi database schema.
- Không đổi API production.
- Không đổi UI production.
- Không tích hợp model vào runtime.
- Không dùng LLM.
- Không fine-tune.
- Không thêm vector database.

## Vì sao cần

Các phase 9.x đã chứng minh CareerOS AI có thể train prototype model và chạy ablation, nhưng metadata còn rải rác giữa scripts, reports và artifacts. Phase 10.0 chuẩn hóa nền tảng để các phase sau quản lý dataset/model/experiment có version rõ ràng hơn.

## Giới hạn

- Registry hiện là JSON local, chưa phải model registry service.
- Chưa có real beta dataset version.
- Chưa có deployment gate tự động.
- Chưa có training orchestration.
- Chưa có model promotion workflow.

## Recommendation

Phase 10.1 nên tập trung vào dataset promotion workflow: thêm real beta labels đã ẩn danh, tạo dataset version mới và chuẩn hóa tiêu chí khi nào một dataset đủ điều kiện dùng cho training/evaluation nghiêm túc.
