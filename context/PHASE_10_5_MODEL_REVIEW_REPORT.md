# Phase 10.5 - Model Registry Review Gate

Date: 2026-06-27

## Mục tiêu

Phase 10.5 thêm review gate giữa registry draft và model candidate. Gate chỉ review metadata/artifacts offline, không train model, không inference, không deploy và không thay production scoring.

## Workflow

```text
Training Job
↓
Registry Draft
↓
Review Gate
↓
Candidate hoặc Rejected
↓
Deployment Decision trong phase tương lai
```

## Thành phần đã thêm

- `backend/app/ml/model_review.py`: review metadata, artifacts, dataset hash, experiment, evaluation và metrics.
- `backend/scripts/review_model_registry.py`: CLI hỗ trợ `--dry-run` và write mode.
- `backend/ml/configs/model_review_config.json`: ngưỡng review có thể cấu hình.
- `backend/tests/test_model_review_gate.py`: tests cho PASS/WARNING/FAIL và các lỗi toàn vẹn.
- `docs/ml/model_review_gate.md`: contract review và production boundary.

## Review rules

Lỗi chặn gồm:

- Registry/artifact/manifest/experiment/evaluation bị thiếu.
- Dataset version hoặc dataset hash không khớp.
- Feature version rỗng.
- Metrics invalid hoặc thấp hơn ngưỡng ngoài warning margin.
- Evaluation report thiếu field bắt buộc.
- Thiếu benchmark results khi config yêu cầu.
- Trùng registry theo `model_version`.
- `production_safe` khác `false`.

Metrics sát ngưỡng trong `warning_margin` tạo WARNING. Không có FAIL thì model có thể thành candidate; mọi FAIL khiến model thành rejected.

## Dry-run behavior

`python scripts/review_model_registry.py --dry-run` chỉ in kết quả review và không sửa registry. Config mặc định trỏ tới registry của `matching_job_contract_v1`; file này chỉ xuất hiện sau khi Training Job Contract được chạy thật.

Ở trạng thái repository hiện tại, chưa có registry/artifact của training job thật vì Phase 10.4 chỉ chạy dry-run. Vì vậy review dry-run báo FAIL `REGISTRY_NOT_FOUND` đúng với production boundary, thay vì tạo candidate giả.

## Write behavior

Write mode:

- Chuyển `candidate` khi outcome là PASS hoặc WARNING.
- Chuyển `rejected` khi outcome là FAIL.
- Ghi `review_history`.
- Luôn giữ `production_safe=false`.
- Không có code path chuyển `production`.

## Giới hạn

- Registry vẫn là JSON local, chưa có chữ ký artifact hoặc external storage.
- Benchmark evidence hiện là metadata trong evaluation report; chưa có cross-validation gate nâng cao.
- WARNING vẫn cần con người cân nhắc trước deployment decision.
- Repository chưa có training job artifact thật để tạo candidate trong Phase 10.5.

## Recommendation Phase 10.6

Phase 10.6 nên xây Model Comparison & Deployment Decision Record offline: so sánh candidate với baseline production bằng benchmark/beta evidence, ghi quyết định rõ ràng và vẫn không tự động deploy.
