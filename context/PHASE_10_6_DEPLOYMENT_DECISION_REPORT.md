# Phase 10.6 - Model Comparison & Deployment Decision Record

Date: 2026-06-27

## Mục tiêu

Phase 10.6 tạo workflow so sánh model candidate với production baseline và ghi Deployment Decision Record offline. Phase này không deploy model, không thay production scoring và không thêm runtime inference.

## Workflow

```text
Training Job
↓
Registry Draft
↓
Review Gate
↓
Candidate
↓
Model Comparison
↓
Deployment Decision Record
```

## Thành phần đã thêm

- `backend/app/ml/model_comparison.py`
- `backend/scripts/create_deployment_decision.py`
- `backend/ml/configs/deployment_decision_schema.json`
- `backend/tests/test_deployment_decision.py`
- `docs/ml/deployment_decision.md`
- `backend/ml/decisions/` được dùng làm output directory khi chạy write mode

## Comparison logic

Baseline là `rule_based_matcher_v2.1`. Candidate được đánh giá dựa trên:

- Registry status và `production_safe=false`.
- Accuracy và macro F1 từ evaluation report.
- Benchmark evidence.
- Model review outcome.
- Dataset version/hash.
- Known limitations.

Output gồm `better`, `worse` hoặc `inconclusive`; risk gồm `low`, `medium`, `high`; recommendation gồm `keep_baseline`, `keep_shadow`, `approve_candidate`, `reject_candidate`.

## Dry-run behavior

Dry-run không ghi decision record. Nếu chưa có candidate, script vẫn chạy thành công và trả:

- `comparison_status=inconclusive`
- `risk_level=medium`
- `decision=keep_baseline`
- lý do candidate registry chưa tồn tại hoặc chưa khả dụng

Behavior này phản ánh đúng trạng thái repository hiện tại: Phase 10.4 chưa chạy training thật và Phase 10.5 chưa tạo candidate thật.

## Validation

Decision record bị từ chối nếu:

- Candidate tồn tại nhưng status không phải `candidate`.
- Candidate thiếu `dataset_hash`.
- `risk_level` hoặc `decision` không hợp lệ.
- Write mode thiếu reviewer.
- `production_change_allowed=true`.

## Production boundary

- `production_change_allowed` luôn là `false`.
- `approve_candidate` không đồng nghĩa deploy.
- Không có code path thay `match_score`, `final_score` hoặc runtime matcher.
- Không thay database schema, API production hoặc UI production.

## Giới hạn

- Chưa có candidate thật để so sánh trong repository.
- Candidate metrics chủ yếu đến từ synthetic/benchmark artifact, chưa có real beta labels.
- Chưa có shadow runtime hoặc production traffic evaluation.
- Decision record là JSON local, chưa có chữ ký hoặc approval nhiều người.

## Recommendation Phase 10.7

Phase 10.7 nên chuẩn hóa Model Release Readiness Checklist và immutable decision audit, vẫn chưa tự động deploy. Chỉ nên bàn runtime shadow mode khi có candidate thật, benchmark đầy đủ và beta labels đã review.
