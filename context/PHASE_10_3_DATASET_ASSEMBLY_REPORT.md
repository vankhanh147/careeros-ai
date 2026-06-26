# Phase 10.3 - Dataset Assembly & Export Pipeline

Date: 2026-06-26

## Mục tiêu

Phase 10.3 xây dựng Dataset Assembly Pipeline để gom synthetic dataset, benchmark dataset và approved beta labels thành một training dataset artifact duy nhất. Phase này không train model và không thay đổi production scoring.

## Workflow

```text
Synthetic
↓
Benchmark
↓
Approved Beta
↓
Dataset Assembly
↓
Training Dataset Artifact
↓
Manifest
↓
Fingerprint
↓
Statistics
↓
Training Ready
```

Đã thêm script:

- `backend/scripts/build_training_dataset.py`

Script mặc định đọc:

- `docs/datasets/synthetic/synthetic_cases.json`
- `docs/benchmark-v1/benchmark_cases.md`

Approved beta labels chỉ được đưa vào khi truyền file review labels qua `--beta-reviews`. Phase 10.3 chưa đưa sample review template vào artifact vì đó không phải real beta data.

## Artifact đã sinh

- `backend/ml/datasets/training_dataset_v3.json`
- `backend/ml/datasets/training_dataset_manifest.json`
- `backend/ml/reports/training_dataset_statistics.json`

Kết quả build hiện tại:

- synthetic_count: 300
- benchmark_count: 10
- beta_count: 0
- total_cases: 310
- artifact_hash: `bae979d135761bb1895a6da735aa3a305b9a849ee9a173809cb9fa9c2568c990`

## Validation

Pipeline validate:

- duplicate `case_id`
- duplicate `content_hash`
- thiếu label
- label invalid
- source invalid
- beta review chưa approved/anonymized
- PII signal
- mojibake signal

Nếu có lỗi, script trả exit code khác 0 và không export artifact.

## Statistics

File `backend/ml/reports/training_dataset_statistics.json` hiện ghi:

- role distribution
- category distribution
- label distribution
- seniority distribution
- source distribution
- approved beta percent

Tóm tắt hiện tại:

- labels: good 62, medium 62, weak 95, mismatch 91
- sources: synthetic 300, benchmark 10
- approved beta percent: 0.0

## Giới hạn

- Chưa có approved real beta labels trong artifact.
- Benchmark cases được parse từ markdown table và normalize thành summary-level cases, chưa có CV/JD full text.
- Dataset artifact hiện phục vụ training/evaluation offline, chưa phải production-safe model input.
- Fingerprint dựa trên JSON canonical của payload; nếu `created_at` thay đổi thì hash cũng thay đổi.

## Recommendation Phase 10.4

Phase 10.4 nên tập trung vào training job contract: đọc duy nhất `training_dataset_v3.json`, ghi experiment metadata, ghi model registry draft và không train từ source dataset rời rạc nữa.
