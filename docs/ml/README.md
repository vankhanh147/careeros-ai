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

## Tài liệu Phase 10.5

- `docs/ml/model_review_gate.md`: review rules, candidate criteria và production boundary.
- `backend/app/ml/model_review.py`: module review registry metadata/artifacts offline.
- `backend/scripts/review_model_registry.py`: CLI review hỗ trợ dry-run và write mode.
- `backend/ml/configs/model_review_config.json`: ngưỡng accuracy, macro F1 và benchmark policy.

Model chỉ được xem là candidate sau khi vượt review gate. Candidate vẫn có `production_safe=false` và không được tự động đưa vào runtime.

## Tài liệu Phase 10.6

- `docs/ml/deployment_decision.md`: model comparison, risk assessment và decision record.
- `backend/app/ml/model_comparison.py`: comparison logic offline.
- `backend/scripts/create_deployment_decision.py`: CLI dry-run/write mode.
- `backend/ml/configs/deployment_decision_schema.json`: schema decision record.
- `backend/ml/decisions/`: output directory cho decision records.

Decision record luôn có `production_change_allowed=false`. Phase 10.6 không deploy và không thay runtime.

## Tài liệu Phase 10.7

- `docs/ml/release_readiness.md`: checklist 21 mục cho dataset, training, review, quality và governance.
- `docs/ml/audit_trail.md`: audit lifecycle, dry-run/write mode và production boundary.
- `backend/app/ml/release_audit.py`: checklist validator và audit record builder.
- `backend/scripts/run_release_audit.py`: CLI audit offline.
- `backend/ml/configs/audit_record_schema.json`: schema audit record.
- `backend/ml/audits/`: output directory của audit trail.

Release Ready chỉ có nghĩa quy trình offline đủ bằng chứng. Nó không đồng nghĩa Production.

## Tài liệu Phase 11.0

- `docs/ml/shadow_evaluation.md`: architecture, contract và safety boundary.
- `backend/app/ml/shadow_evaluation.py`: config validator và shadow plan builder.
- `backend/scripts/plan_shadow_evaluation.py`: planning CLI dry-run/write mode.
- `backend/ml/configs/shadow_evaluation_config.json`: config mặc định disabled.
- `backend/ml/configs/shadow_disagreement_schema.json`: schema disagreement future-only.

Phase 11.0 chưa chạy shadow inference. Mọi plan đều giữ `runtime_activation_allowed=false` và production tiếp tục dùng rule-based matcher.
