# Phase 11.5 - Dataset Promotion Planning Bridge

Date: 2026-06-29

## Mục tiêu

Phase 11.5 tạo bridge offline để lập Dataset Promotion plan từ Label Review Draft QA evidence. Bridge không promote dataset và không train model.

## Workflow

```text
Shadow Review
↓
Label Review QA
↓
Promotion Planning
↓
Dataset Promotion trong phase tương lai
↓
Training trong phase tương lai
```

## Thành phần

- `backend/app/ml/dataset_promotion_bridge.py`
- `backend/scripts/build_dataset_promotion_plan.py`
- `backend/tests/test_dataset_promotion_bridge.py`
- `docs/ml/dataset_promotion_bridge.md`

## Planning

Plan tổng hợp total, promotion-ready, blocked cases, blockers, target dataset version và estimated size. Current `dataset_v3` được suy ra thành target `dataset_v4`.

## No-report behavior

Nếu chưa có QA report, CLI trả `no_qa_report`, recommendation chạy Label Review Draft QA Bridge write mode trước, không crash và không ghi plan.

## Validation

Bridge revalidate source draft bằng validator Phase 10.2; kiểm tra stale QA, workflow approval, anonymization, reviewer, confidence, duplicate cases/export/labels, dataset version, UTF-8, BOM, PII và mojibake.

## Safety boundary

- `promotion_allowed` chỉ là planning eligibility.
- `promotion_executed=false`.
- `training_allowed=false`.
- Không sửa QA report, draft hoặc manifest.
- Không dataset promotion, training, runtime inference hoặc production changes.

## Giới hạn

- Repository chưa có QA report thật.
- Chưa có promotion-ready real beta labels.
- Duplicate export check dùng plan file local hiện tại.
- Estimated size chỉ cộng ready cases vào current manifest size.

## Recommendation Phase 11.6

Phase 11.6 nên tạo Promotion Approval Record/Audit offline trước khi cho phép con người chạy Dataset Promotion Workflow. Không tự động promote hoặc train.
