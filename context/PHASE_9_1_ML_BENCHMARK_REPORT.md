# Phase 9.1 - ML Benchmark & Disagreement Analysis

Date: 2026-06-22

## Mục tiêu

Đánh giá Trainable Matching Model V1 bằng benchmark U01-U10 và Synthetic Dataset V2. Phase này không train model mới, không thay production scoring và không đưa ML prediction thành điểm chính.

## U01-U10 comparison

| Case | Scenario | Expected range | Expected label | Rule score | Hybrid candidate | ML label | ML confidence | Agreement |
| --- | --- | --- | --- | ---: | ---: | --- | ---: | --- |
| U01 | .NET Backend Intern -> .NET Backend JD | 75-90 | good | 84.4 | 84.4 | good | 0.345 | needs_review |
| U02 | Node.js Backend -> .NET Backend JD | 50-70 | medium | 58.6 | 58.6 | good | 0.330 | needs_review |
| U03 | React Frontend -> React Frontend JD | 80-90 | good | 81.1 | 81.1 | good | 0.420 | needs_review |
| U04 | React Frontend -> .NET Backend JD | 25-50 | weak | 31.4 | 31.4 | good | 0.360 | needs_review |
| U05 | AI/Python Backend -> .NET Backend JD | 35-60 | medium | 60.0 | 60.0 | good | 0.338 | needs_review |
| U06 | .NET Backend -> React Frontend JD | 25-50 | weak | 29.7 | 29.7 | good | 0.372 | needs_review |
| U07 | Flutter Mobile -> AI/ML JD | 35-60 | weak | 33.5 | 33.5 | good | 0.358 | needs_review |
| U08 | Data Analyst -> .NET Backend JD | 35-60 | weak | 31.0 | 31.0 | good | 0.303 | needs_review |
| U09 | Cybersecurity -> React Frontend JD | 25-50 | weak | 37.2 | 37.2 | good | 0.358 | needs_review |
| U10 | Marketing/Business -> .NET Backend JD | 10-35 | mismatch | 12.8 | 12.8 | good | 0.323 | needs_review |

## Disagreement summary

- Tổng trạng thái: needs_review: 10
- `aligned`: rule-based score, expected label và ML label cùng hướng.
- `minor_disagreement`: ML lệch một bậc so với expected/rule label.
- `major_disagreement`: ML lệch mạnh, cần review trước khi tin.
- `needs_review`: ML confidence thấp hoặc artifact không khả dụng.

## Synthetic Dataset V2 error analysis

- Test size: 75
- `good -> medium`: 8
- `mismatch -> medium`: 11
- `medium -> good`: 1
- `medium -> weak`: 0
- `medium -> mismatch`: 0

### Category error summary

| Category | Errors | Total test cases | Error rate |
| --- | ---: | ---: | ---: |
| role_mismatch | 11 | 11 | 1.0 |
| exact_fit | 8 | 8 | 1.0 |
| cross_domain_transferable | 1 | 8 | 0.125 |
| career_switch | 0 | 4 | 0.0 |
| keyword_stuffing | 0 | 8 | 0.0 |
| missing_critical_skill | 0 | 8 | 0.0 |
| non_it_mismatch | 0 | 8 | 0.0 |
| same_role_different_stack | 0 | 7 | 0.0 |
| strong_evidence | 0 | 7 | 0.0 |
| weak_cv | 0 | 6 | 0.0 |

## Model reliability assessment

ML V1 hữu ích như tín hiệu phụ để phát hiện disagreement, nhưng chưa đủ tin cậy để thay matcher hiện tại. Kết quả Phase 9.0 và Phase 9.1 cùng cho thấy model nhận diện `weak` khá ổn, nhưng còn dễ kéo `good` và `mismatch` về `medium`.

## Khi có thể tin ML

- Khi ML label trùng với rule-based score band và confidence đủ cao.
- Khi ML dùng để gợi ý case cần review nội bộ, không dùng trực tiếp cho user-facing score.
- Khi dữ liệu input giống format synthetic summary đã train.

## Khi không nên tin ML

- Khi ML confidence thấp.
- Khi ML label trái ngược mạnh với rule-based score hoặc benchmark expected label.
- Khi CV/JD là raw artifact dài, nhiễu, khác nhiều so với synthetic summary.
- Khi case liên quan career switch, same-role different-stack hoặc mismatch tinh tế.

## Recommendation trước Phase 9.2

1. Không promote ML V1 thành production score.
2. Dùng disagreement report để chọn case cần human review.
3. Bổ sung real anonymized beta labels cho boundary `good/medium` và `mismatch/medium`.
4. Nếu cải thiện model, ưu tiên dataset quality và label review trước khi đổi thuật toán.
5. Giữ rule-based matcher là source of truth cho user-facing score.
