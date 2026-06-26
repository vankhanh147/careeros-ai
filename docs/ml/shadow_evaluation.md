# Shadow Evaluation Architecture

## Shadow evaluation là gì

Shadow evaluation là cơ chế đánh giá candidate model song song với production matcher. Production vẫn dùng `rule_based_matcher_v2.1`; shadow output chỉ phục vụ đánh giá nội bộ và không được thay `match_score`, `final_score` hoặc nội dung user nhìn thấy.

Phase 11.0 chỉ xây contract, config, validator và planning CLI. Chưa có runtime shadow inference.

## Khi nào được cân nhắc bật

Chỉ cân nhắc mode `shadow` khi:

- Có registry `status=candidate`.
- Candidate đã qua model review và deployment decision.
- Dataset hash, benchmark và release audit có thể truy vết.
- Config giữ mọi safety invariant.
- Có latency budget và rollback owner rõ ràng.

## Input contract

Config nằm tại `backend/ml/configs/shadow_evaluation_config.json`:

- `enabled`
- `candidate_model_version`
- `candidate_registry_path`
- `mode`: `disabled`, `dry_run`, `shadow`
- `sample_rate`
- `max_latency_ms`
- `log_disagreements_only`
- `store_raw_text`
- `production_score_source`
- `allow_user_facing_output`

## Output contract

Planning output gồm:

- requested/effective mode
- candidate status
- sample rate và latency budget
- safety checks
- warnings
- recommendation
- `runtime_activation_allowed=false`

Write mode chỉ ghi `backend/ml/reports/shadow_evaluation_plan.json`; nó không sửa production config và không chạy model.

## Production boundary

- Production score source luôn là `rule_based`.
- Shadow output không được đưa vào API response user-facing.
- Candidate không được thay đổi suggestion, skill gap, roadmap hoặc interview.
- `effective_enabled=false` trong toàn bộ Phase 11.0.

## Rollback boundary

Khi runtime shadow được thiết kế ở phase tương lai, phải có kill switch độc lập. Shadow phải tắt ngay mà không ảnh hưởng production matcher. Nếu shadow lỗi, timeout hoặc thiếu artifact, request vẫn tiếp tục bằng rule-based flow.

## Logging boundary

- Chỉ log disagreement metadata khi được cho phép.
- Không log full CV/JD.
- Không log JWT, email hoặc identifiers không cần thiết.
- Future disagreement record phải theo `shadow_disagreement_schema.json`.

## Privacy boundary

- `store_raw_text=false` là invariant.
- Chỉ lưu score, prediction, severity và internal IDs tối thiểu.
- Không gửi CV/JD sang external API.
- Không dùng dữ liệu shadow làm training label nếu chưa anonymize và human review.

## Khi nào phải tắt shadow

- Latency vượt `max_latency_ms`.
- Candidate artifact load fail hoặc registry mất trạng thái candidate.
- Có nguy cơ raw text/PII bị ghi log.
- Shadow output xuất hiện trong user-facing response.
- Disagreement bất thường hoặc model drift chưa được review.
- Production matcher bị ảnh hưởng về availability.

## No-candidate behavior

Thiếu candidate không làm app crash. Validator trả plan `disabled` với WARNING và recommendation hoàn tất training/review trước. Không có fallback sang model khác.
