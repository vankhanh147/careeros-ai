# Training Dataset Assembly

## Mục tiêu

Training Dataset Assembly là bước gom dữ liệu đã được kiểm soát thành một artifact duy nhất để dùng cho các phase training/evaluation tiếp theo của CareerOS AI.

Pipeline này không train model, không thay production scoring và không tích hợp runtime.

## Nguồn dữ liệu

Script assembly đọc các nguồn sau:

- Synthetic dataset: `docs/datasets/synthetic/synthetic_cases.json`
- Benchmark dataset: `docs/benchmark-v1/benchmark_cases.md`
- Approved beta labels: chỉ thêm khi truyền file review labels đã approved qua tham số `--beta-reviews`

Mặc định Phase 10.3 chưa đưa beta template vào training dataset vì chưa có real beta labels đã review.

## Artifact export

Lệnh chạy từ thư mục `backend/`:

```bash
python scripts/build_training_dataset.py
```

Output:

- `backend/ml/datasets/training_dataset_v3.json`
- `backend/ml/datasets/training_dataset_manifest.json`
- `backend/ml/reports/training_dataset_statistics.json`

Dry-run:

```bash
python scripts/build_training_dataset.py --dry-run
```

Dry-run chỉ validate và in kế hoạch, không ghi artifact, manifest hoặc statistics.

## Validation

Assembly sẽ dừng và không export nếu phát hiện:

- `case_id` bị trùng.
- `content_hash` bị trùng.
- Thiếu label.
- Label không thuộc `good`, `medium`, `weak`, `mismatch`.
- Source không thuộc `synthetic`, `benchmark`, `beta`.
- Beta case chưa approved hoặc chưa anonymized.
- Dữ liệu có dấu hiệu PII.
- Dữ liệu có dấu hiệu mojibake.

## Manifest

Manifest ghi lại:

- `dataset_version`
- `created_at`
- `synthetic_count`
- `benchmark_count`
- `beta_count`
- `total_cases`
- `source_files`
- `artifact_name`
- `artifact_hash`
- `notes`

## Fingerprint

`artifact_hash` là SHA256 của payload JSON canonical. Hash này giúp biết artifact training có thay đổi hay không giữa các lần build.

## Statistics

Statistics gồm:

- role distribution
- category distribution
- label distribution
- seniority distribution
- source distribution
- approved beta percent

## Ranh giới production

- Không train model.
- Không thay `match_score`.
- Không thay `final_score`.
- Không đổi database schema.
- Không đổi API production.
- Không đổi UI production.
- Không thêm LLM hoặc vector database.
