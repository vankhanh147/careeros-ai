# Phase 9.2 - Hybrid Feature Evaluation

Date: 2026-06-24T17:25:51.341026+00:00

## Mục tiêu

So sánh model text-only V1 với model hybrid dùng TF-IDF text features và structured features từ rule-based matcher, taxonomy, semantic/hybrid metadata và dataset metadata. Phase này chỉ là offline evaluation, không thay production scoring.

## So sánh metrics

| Model | Accuracy | Macro F1 | good -> medium | mismatch -> medium | weak errors |
| --- | ---: | ---: | ---: | ---: | ---: |
| Text-only V1 | 0.733 | 0.719 | 8 | 11 | 0 |
| Hybrid feature model | 0.947 | 0.947 | 0 | 4 | 0 |

## Confusion matrix của Text-only V1

| Actual \ Predicted | good | medium | mismatch | weak |
|---|---|---|---|---|
| good | 7 | 8 | 0 | 0 |
| medium | 1 | 14 | 0 | 0 |
| mismatch | 0 | 11 | 12 | 0 |
| weak | 0 | 0 | 0 | 22 |

## Confusion matrix của Hybrid model

| Actual \ Predicted | good | medium | mismatch | weak |
|---|---|---|---|---|
| good | 15 | 0 | 0 | 0 |
| medium | 0 | 15 | 0 | 0 |
| mismatch | 0 | 4 | 19 | 0 |
| weak | 0 | 0 | 0 | 22 |

## Tổng hợp lỗi theo category của Hybrid model

| Category | Errors | Total | Error rate |
| --- | ---: | ---: | ---: |
| career_switch | 0 | 4 | 0.0 |
| cross_domain_transferable | 0 | 8 | 0.0 |
| exact_fit | 0 | 8 | 0.0 |
| keyword_stuffing | 0 | 8 | 0.0 |
| missing_critical_skill | 0 | 8 | 0.0 |
| non_it_mismatch | 0 | 8 | 0.0 |
| role_mismatch | 4 | 11 | 0.364 |
| same_role_different_stack | 0 | 7 | 0.0 |
| strong_evidence | 0 | 7 | 0.0 |
| weak_cv | 0 | 6 | 0.0 |

## Nhận xét

- Hybrid model dùng thêm tín hiệu từ matcher nên kỳ vọng giảm lỗi boundary `good -> medium` và `mismatch -> medium`.
- Nếu metrics cải thiện nhưng phụ thuộc quá nhiều vào `rule_based_score`, model vẫn chỉ nên được xem là evaluator phụ, không phải replacement cho matcher.
- Semantic đang disabled trong môi trường hiện tại nên `semantic_available=0` và `semantic_similarity=0` cho dataset được build ở phase này.

## Kết luận

Hybrid feature model là bước tốt hơn text-only để học từ tri thức rule-based hiện có. Tuy nhiên, dữ liệu vẫn là synthetic nên chưa đủ cơ sở để đưa vào production scoring.
