# Phase 11.4 - Label Review Draft QA Bridge

Date: 2026-06-28

## Mục tiêu

Phase 11.4 tạo bridge offline để validate Shadow Label Review Draft bằng Label Review validator hiện có và tạo promotion readiness summary.

## Workflow

```text
Shadow Label Review Draft
↓
Label Review QA Bridge
↓
Validation Summary
↓
Promotion Readiness Plan
↓
Dataset Promotion trong phase sau
```

## Thành phần

- `backend/app/ml/label_review_bridge.py`
- `backend/scripts/validate_shadow_label_review_draft.py`
- `backend/tests/test_label_review_bridge.py`
- `docs/ml/label_review_bridge.md`

## No-draft behavior

Nếu chưa có `shadow_label_review_draft.json`, CLI trả `no_draft`, recommendation `run shadow review resolution export first`, không crash và không ghi QA report.

## Validation

Bridge gọi trực tiếp `validate_label_review_cases` Phase 10.2. Summary bổ sung promotion blockers cho validation errors, zero ready cases, invalid training approval, anonymization, reviewer và confidence.

## Promotion readiness

- Draft `UNDER_REVIEW` hợp lệ: ready for review, chưa ready for promotion.
- Case chỉ promotion-ready khi đạt workflow status và approved training metadata hợp lệ.
- Bridge luôn giữ `promotion_allowed=false` và `training_allowed=false`.
- Bridge không sửa input draft.

## Giới hạn

- Repository chưa có Shadow Label Review Draft thật.
- Chưa có approved real beta labels.
- QA report là JSON offline, chưa có UI.
- Bridge chưa tạo Dataset Promotion config.

## Recommendation Phase 11.5

Phase 11.5 nên tạo Dataset Promotion Planning Bridge ở chế độ dry-run, chỉ nhận QA report promotion-ready và vẫn không tự động promote hoặc train model.
