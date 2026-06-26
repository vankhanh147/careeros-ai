# Phase 11.0 - Shadow Evaluation Architecture & Safety Boundary

Date: 2026-06-27

## Mục tiêu

Phase 11.0 xây kiến trúc và safety boundary cho shadow evaluation. Production tiếp tục dùng rule-based matcher; phase này không chạy runtime inference và không đưa ML output tới user.

## Architecture

```text
Rule-based production
↓
Shadow config
↓
Shadow safety validator
↓
Candidate check
↓
Shadow plan
↓
Future disagreement schema
```

## Thành phần

- `backend/app/ml/shadow_evaluation.py`
- `backend/scripts/plan_shadow_evaluation.py`
- `backend/ml/configs/shadow_evaluation_config.json`
- `backend/ml/configs/shadow_disagreement_schema.json`
- `backend/tests/test_shadow_evaluation.py`
- `docs/ml/shadow_evaluation.md`

## Safety rules

- `allow_user_facing_output=false`.
- `store_raw_text=false`.
- `production_score_source=rule_based`.
- `sample_rate` trong `0..1`.
- `max_latency_ms` là số nguyên dương.
- Mode shadow yêu cầu registry status candidate, model version khớp và `production_safe=false`.
- Mọi plan giữ `runtime_activation_allowed=false`.

## Config defaults

Config mặc định:

- `enabled=false`
- `mode=disabled`
- `sample_rate=0.0`
- `store_raw_text=false`
- `allow_user_facing_output=false`
- `production_score_source=rule_based`

## Validator behavior

Vi phạm safety invariant bị reject ngay. Thiếu candidate hoặc registry không hợp lệ không làm crash; plan được hạ về disabled và trả WARNING.

## No-candidate behavior

Repository hiện chưa có candidate thật. Dry-run mặc định tạo plan disabled an toàn, không ghi file và không chạy inference.

## Production boundary

- Không đổi production scoring, `match_score` hoặc `final_score`.
- Không đổi database schema, API production hoặc UI production.
- Không deploy model.
- Không có runtime shadow inference.
- Disagreement schema chỉ là contract tương lai, chưa có runtime logging.

## Giới hạn

- Chưa đo latency model thật.
- Chưa có candidate artifact thật.
- Chưa có disagreement logging hoặc storage.
- Chưa có kill switch runtime vì shadow runtime chưa tồn tại.

## Recommendation Phase 11.1

Chỉ cân nhắc Phase 11.1 khi có candidate thật vượt release audit. Phase tiếp theo nên xây offline shadow harness trên benchmark/beta-safe inputs trước, chưa tích hợp request path production.
