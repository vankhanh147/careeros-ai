# Phase 10.4 - Training Job Contract

Date: 2026-06-26

## Mục tiêu

Chuẩn hóa Training Job Contract để mọi training sau này đọc từ training dataset artifact đã assembly, không đọc trực tiếp từ source dataset rời rạc. Phase này không đổi production scoring, `match_score`, `final_score`, database schema, API production hoặc UI production.

## Đã thêm

### Training job contract

Tài liệu mới:

- `docs/ml/training_job_contract.md`

Contract định nghĩa:

- Input dataset artifact bắt buộc.
- Manifest và artifact hash bắt buộc.
- Training config bắt buộc.
- Output model artifacts, experiment record, registry draft và evaluation report.
- Exit code rules.
- Validation rules.

### Training job runner

Script mới:

- `backend/scripts/run_training_job.py`

Runner hiện hỗ trợ:

- Đọc `backend/ml/configs/training_config.json`.
- Đọc `backend/ml/datasets/training_dataset_v3.json`.
- Đọc `backend/ml/datasets/training_dataset_manifest.json`.
- Validate SHA256 artifact hash.
- Validate dataset version giữa config, artifact và manifest.
- Validate label, duplicate model version, PII và mojibake.
- Dry-run mode không ghi artifact.
- Chạy thật để tạo model artifacts, experiment record, registry draft và evaluation report nếu cần.

### Training config

Cập nhật:

- `dataset_version`: `dataset_v3`
- `classifier`: `LogisticRegression`
- `model_name`: `matching_job_contract`
- `model_version`: `matching_job_contract_v1`

Config này chỉ dùng cho offline training job, không dùng để thay production scoring.

## Input / Output

Input duy nhất của training job:

- `backend/ml/datasets/training_dataset_v3.json`
- `backend/ml/datasets/training_dataset_manifest.json`
- `backend/ml/configs/training_config.json`

Output khi chạy thật:

- `backend/ml/models/{model_version}/model.joblib`
- `backend/ml/models/{model_version}/vectorizer.joblib`
- `backend/ml/models/{model_version}/labels.json`
- `backend/ml/models/{model_version}/model_metadata.json`
- `backend/ml/experiments/{run_id}.json`
- `backend/ml/registry/{model_version}.json`
- `backend/ml/reports/{run_id}_evaluation.json`

## Artifact behavior

- Dry-run không ghi file mới.
- Chạy thật không overwrite model version đã tồn tại.
- Registry draft luôn có `production_safe=false`.
- Model artifact không được tự động đưa vào runtime.

## Validation rules

Training job fail nếu:

- Thiếu artifact hoặc manifest.
- `artifact_hash` không khớp manifest.
- `dataset_version` không khớp.
- Dataset rỗng.
- Label invalid.
- `model_version` đã tồn tại.
- Có PII hoặc mojibake.
- Config thiếu field bắt buộc.

## Tests đã thêm

File mới:

- `backend/tests/test_training_job_contract.py`

Tests kiểm tra:

- Load training config.
- Validate dataset hash.
- Fail khi hash mismatch.
- Fail khi duplicate model version.
- Dry-run không ghi artifact.
- Real run trong `tmp_path` sinh metadata và artifacts đầy đủ.

## Giới hạn

- Runner hiện dùng `LogisticRegression` để giữ baseline đơn giản, deterministic và nhẹ.
- Chưa productionize model.
- Chưa dùng approved beta labels thật vì artifact hiện có `beta_count=0`.
- Chưa thêm model comparison hoặc approval gate; đây là scope Phase 10.5+.

## Recommendation Phase 10.5

Phase 10.5 nên tập trung vào Model Registry Review Gate: so sánh registry draft, kiểm tra metrics tối thiểu, benchmark, dataset hash và quyết định model có đủ điều kiện được promote sang candidate hay không.
