# Label Review Draft QA Bridge

## Mục tiêu

QA Bridge nối Shadow Label Review Draft với validator Label Review Pipeline hiện có. Bridge chỉ đọc draft, chạy validation và tạo promotion readiness plan; không sửa draft, không approve label và không promote dataset.

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

## Input

```text
backend/ml/reviews/shadow_label_review_draft.json
```

Bridge đọc `cases` do Shadow Review Resolution Export tạo và gọi trực tiếp `validate_label_review_cases` trong `backend/app/ml/training_infra.py`.

## Output

Write mode tạo:

```text
backend/ml/reports/shadow_label_review_draft_qa.json
```

Summary gồm:

- Total cases.
- Errors/warnings count.
- Ready for review.
- Ready for promotion count.
- Ready for promotion.
- Not ready.
- Promotion blockers.
- Recommendation.
- Case validation results.

## Readiness rules

Draft bị chặn promotion khi:

- Có validation errors.
- Không có case promotion-ready.
- Training approval không phù hợp workflow status.
- Case chưa anonymized.
- Thiếu reviewer.
- Label confidence ngoài `0..1`.
- Có PII hoặc mojibake.

Draft hợp lệ ở `UNDER_REVIEW` có thể `ready_for_review=true` nhưng vẫn `ready_for_promotion=false`.

## CLI

Dry-run:

```bash
python scripts/validate_shadow_label_review_draft.py --dry-run
```

Write mode:

```bash
python scripts/validate_shadow_label_review_draft.py
```

Nếu chưa có draft, CLI trả `no_draft`, recommendation `run shadow review resolution export first`, không crash và không ghi report.

## Safety boundary

- Bridge không sửa draft.
- Bridge không set `approved_for_training`.
- `promotion_allowed=false`.
- `training_allowed=false`.
- Không chứa hoặc xuất raw CV/JD text.
- Không train model hoặc thay production behavior.
