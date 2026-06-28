# Phase 11.1 - Offline Shadow Evaluation Harness

Date: 2026-06-28

## Mục tiêu

Phase 11.1 tạo harness offline để so sánh rule-based, hybrid signal và candidate ML trên training dataset artifact. Harness không chạy trong production request và không ảnh hưởng user.

## Workflow

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

## Thành phần

- `backend/app/ml/shadow_harness.py`
- `backend/scripts/run_shadow_harness.py`
- `backend/tests/test_shadow_harness.py`
- `docs/ml/shadow_harness.md`

## Comparison metrics

- Agreement/disagreement count và rate giữa rule, hybrid và ML.
- Candidate better/rule better dựa trên khoảng cách label tới expected label.
- Inconclusive count.
- Average candidate confidence.
- Review required count.
- Confusion summary expected label → ML label.

## Report structure

Write mode sinh `backend/ml/reports/shadow_summary.json`. Report gồm dataset/candidate metadata, source distribution, metrics tổng hợp và comparison records không chứa raw CV/JD text.

## No-candidate behavior

Repository hiện chưa có registry candidate thật. Harness không dùng prototype artifacts cũ làm candidate. Dry-run chạy ở `baseline_only`, recommendation `keep baseline`, không crash và không ghi report.

## Safety boundary

- Production score source giữ `rule_based`.
- `production_change_allowed=false`.
- `stored_raw_text=false`.
- Không thay API/UI/database schema.
- Không runtime shadow hoặc production inference.

## Giới hạn

- Candidate comparison chưa chạy trên artifact candidate thật.
- Dataset hiện không có approved real beta labels.
- Rule-based evaluation trên summary text không hoàn toàn tương đương raw CV/JD.
- Human review chưa có UI; sử dụng comparison records offline.

## Recommendation Phase 11.2

Chỉ bắt đầu Phase 11.2 khi có candidate thật vượt release audit. Phase tiếp theo nên chuẩn hóa disagreement review queue offline và acceptance thresholds; chưa tích hợp production request path.
