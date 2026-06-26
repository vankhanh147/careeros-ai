# CareerOS AI ML Infrastructure

Tài liệu này mô tả nền tảng AI Training Infrastructure của CareerOS AI từ Phase 10.0.

## Mục tiêu

CareerOS AI cần một quy trình rõ ràng cho vòng đời model:

```text
Dataset
↓
Training
↓
Evaluation
↓
Model Registry
↓
Versioning
↓
Deployment decision
```

Phase 10.0 chỉ tạo foundation. Không model nào được đưa vào production scoring trong phase này.

## Thành phần chính

- Dataset versioning: quản lý nguồn dữ liệu và số lượng case theo version.
- Dataset promotion: tạo dataset version mới bằng dry-run/write workflow có validation.
- Label review & QA: kiểm tra beta/training labels đã ẩn danh, có human review và đủ điều kiện promote.
- Model registry: lưu metadata model artifact và metrics.
- Experiment tracking: ghi lại thử nghiệm training/evaluation offline.
- Training config: chuẩn hóa seed, split ratio, feature version và classifier.
- Evaluation report format: chuẩn hóa accuracy, macro F1, confusion matrix, precision, recall và error analysis.
- Training dataset assembly: gom synthetic, benchmark và approved beta labels thành một artifact training duy nhất.

## Ranh giới production

- Không thay `match_score`.
- Không thay `final_score`.
- Không đổi database schema.
- Không đổi API production.
- Không đổi UI production.
- Không thêm LLM, fine-tuning hoặc vector database.

## Thư mục liên quan

- `backend/ml/`: workspace metadata offline.
- `backend/app/ml/training_infra.py`: parser/validator metadata.
- `docs/ml/`: tài liệu quy trình.
- `context/PHASE_10_0_TRAINING_INFRA_REPORT.md`: report Phase 10.0.

## Tài liệu Phase 10.2

- `docs/ml/label_review_schema.md`: schema metadata và workflow trạng thái label review.
- `docs/ml/label_quality.md`: nguyên tắc quality label, human review và không train từ feedback thô.
- `backend/scripts/validate_label_review_pipeline.py`: script QA offline cho review cases.

## Tài liệu Phase 10.3

- docs/ml/training_dataset.md: workflow assembly, validation, manifest, fingerprint và statistics.
- backend/scripts/build_training_dataset.py: script build training dataset artifact offline.
- backend/ml/datasets/training_dataset_v3.json: artifact training dataset hiện tại.

## Tài liệu Phase 10.4

- `docs/ml/training_job_contract.md`: contract bắt buộc cho mọi training job mới.
- `backend/scripts/run_training_job.py`: runner offline đọc training dataset artifact, manifest và training config.
- `backend/ml/configs/training_config.json`: config hiện trỏ tới `dataset_v3` và `matching_job_contract_v1`.

Từ Phase 10.4, training script mới không được đọc trực tiếp từ synthetic/benchmark/beta raw sources. Training phải đi qua artifact `backend/ml/datasets/training_dataset_v3.json` và manifest tương ứng.
