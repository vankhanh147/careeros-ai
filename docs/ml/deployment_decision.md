# Model Comparison & Deployment Decision Record

## Mục tiêu

Deployment Decision Record ghi lại bằng chứng và lý do khi so sánh model candidate với production baseline. Phase 10.6 chỉ tạo quyết định offline, không deploy và không thay production scoring.

```text
Registry Candidate
↓
Model Comparison
↓
Risk Assessment
↓
Deployment Decision Record
↓
Runtime/Production Decision trong phase tương lai
```

## Production baseline

Baseline hiện tại là `rule_based_matcher_v2.1`: matcher production explainable, deterministic và đã được kiểm tra bằng benchmark U01-U10. Metrics phân loại của candidate không được so sánh trực tiếp với `match_score`; candidate chỉ được đánh giá tốt hơn khi có đủ metrics gate, benchmark evidence và model review outcome.

## Comparison output

- `comparison_status`: `better`, `worse`, `inconclusive`.
- `risk_level`: `low`, `medium`, `high`.
- `recommendation`: `keep_baseline`, `keep_shadow`, `approve_candidate`, `reject_candidate`.

`approve_candidate` chỉ là chấp thuận candidate cho bước quyết định tiếp theo, không phải quyền thay production.

## Risk levels

- `low`: metrics tốt, benchmark evidence đầy đủ, review PASS.
- `medium`: tín hiệu tốt nhưng còn giới hạn hoặc cần shadow evaluation.
- `high`: metrics thấp, thiếu review hoặc thiếu bằng chứng quan trọng.

## Decision record

Schema nằm tại `backend/ml/configs/deployment_decision_schema.json`. Mọi record phải có reviewer trong write mode và luôn có:

```json
{
  "production_change_allowed": false
}
```

Record được ghi vào `backend/ml/decisions/{decision_id}.json`. File cũ không bị overwrite.

## Dry-run

```bash
python scripts/create_deployment_decision.py --dry-run
```

Nếu chưa có candidate, dry-run vẫn hoàn tất với:

- `comparison_status=inconclusive`
- `recommendation=keep_baseline`
- lý do không có candidate khả dụng

Dry-run không ghi file.

## Write mode

```bash
python scripts/create_deployment_decision.py --reviewer "founder-review"
```

Write mode yêu cầu registry có `status=candidate`, có `dataset_hash` và reviewer không rỗng. Phase 10.6 không hỗ trợ deployment hoặc runtime integration.
