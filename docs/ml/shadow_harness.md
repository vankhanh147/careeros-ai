# Offline Shadow Evaluation Harness

## Mục tiêu

Offline Shadow Evaluation Harness so sánh rule-based matcher, hybrid candidate signal và candidate ML trên training dataset artifact. Harness không chạy trong production request, không thay user-facing score và không ghi raw CV/JD text.

```text
Offline Dataset
↓
Rule-based Prediction
↓
Candidate Prediction
↓
Comparison
↓
Shadow Report
↓
Human Review
↓
Decision
```

## Input

- `backend/ml/datasets/training_dataset_v3.json`
- `backend/ml/configs/shadow_evaluation_config.json`
- Candidate registry tùy chọn có `status=candidate`
- Model/vectorizer artifacts được registry tham chiếu

Dataset artifact đã chứa synthetic cases và benchmark U01-U10. Harness thống kê riêng số case `source=benchmark`.

## Comparison workflow

Với mỗi case, harness ghi:

- Expected label.
- Rule-based score và label.
- Hybrid label.
- Candidate ML label và confidence nếu có.
- Candidate better, rule better hoặc inconclusive.
- Có cần human review hay không.

Comparison record chỉ lưu `case_id` và metadata đánh giá. Không lưu `resume_summary` hoặc `job_description_summary`.

## Metrics

Shadow summary gồm:

- Total cases và benchmark cases.
- Agreement/disagreement count và rate.
- Candidate better.
- Rule better.
- Inconclusive.
- Average candidate confidence.
- Human review required count.
- Confusion summary theo expected label và ML label.

Agreement yêu cầu rule, hybrid và ML cùng label. Candidate/rule better được tính theo khoảng cách thứ bậc tới expected label.

## Baseline-only behavior

Nếu không có candidate registry/artifact:

- Harness vẫn chạy rule-based/hybrid trên dataset.
- `status=baseline_only`.
- ML fields là null.
- Recommendation là `keep baseline`.
- Không crash và không tự dùng prototype model cũ.

## Chạy dry-run

```bash
python scripts/run_shadow_harness.py --dry-run
```

Dry-run tính report nhưng không ghi file.

Write mode:

```bash
python scripts/run_shadow_harness.py
```

Write mode ghi `backend/ml/reports/shadow_summary.json`. Đây vẫn là offline report, không kích hoạt runtime shadow.

## Human review workflow

1. Lọc records có `review_required=true`.
2. Review role/stack mismatch, expected label và evidence.
3. Không dùng disagreement làm training label trực tiếp.
4. Anonymize và đưa case qua label review trước dataset promotion.
5. Tạo deployment decision mới chỉ sau khi evidence đủ.

## Safety boundary

- Production score source luôn là rule-based.
- `production_change_allowed=false`.
- `stored_raw_text=false`.
- Không có API/UI integration.
- Không load candidate nếu registry chưa có status candidate.
