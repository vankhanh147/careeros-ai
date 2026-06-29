# Dataset Promotion Planning Bridge

## Mục tiêu

Promotion Planning Bridge đọc Label Review Draft QA report, revalidate source draft và lập kế hoạch cho một dataset version tương lai. Bridge không promote dataset và không train model.

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

## Input

QA report mặc định:

```text
backend/ml/reports/shadow_label_review_draft_qa.json
```

Bridge theo `source_draft` trong QA report để revalidate cases và đọc current dataset manifest:

```text
backend/ml/datasets/training_dataset_manifest.json
```

## Planning summary

Plan gồm:

- Total cases.
- Promotion-ready cases.
- Blocked cases.
- Blockers.
- Current/target dataset version.
- Estimated dataset size.
- Recommendation.
- `promotion_allowed`.
- `promotion_executed=false`.
- `training_allowed=false`.

## Promotion readiness

`promotion_allowed=true` chỉ khi:

- QA errors bằng 0.
- QA report không có blockers.
- Có ít nhất một promotion-ready case.
- Fresh Label Review validation không có lỗi.
- Case status/approval/anonymization/reviewer/confidence hợp lệ.
- Không duplicate case/export/label.
- Dataset version có dạng `dataset_vN`.
- UTF-8 hợp lệ, không BOM, PII hoặc mojibake.

Flag này chỉ có nghĩa plan đủ điều kiện để con người chạy Dataset Promotion Workflow sau này.

## Duplicate protection

Bridge chặn:

- Duplicate case ID.
- Duplicate label record.
- Duplicate case trong exported items.
- Cùng `source_export_id` đã xuất hiện trong promotion plan hiện tại.

## CLI

Dry-run:

```bash
python scripts/build_dataset_promotion_plan.py --dry-run
```

Write mode:

```bash
python scripts/build_dataset_promotion_plan.py
```

Output:

```text
backend/ml/reports/dataset_promotion_plan.json
```

Nếu chưa có QA report, CLI trả `no_qa_report`, không crash và không ghi plan.

## Safety boundary

- Không sửa QA report, source draft hoặc manifest.
- Không gọi Dataset Promotion script.
- Không tạo dataset metadata/version mới.
- Không train model.
- Không thay production scoring, API hoặc UI.
