# Phase 9.3 - Hybrid Model Benchmark & Ablation Study

Date: 2026-06-26T04:25:27.692430+00:00

## Mục tiêu

Đánh giá Hybrid Matching Model từ Phase 9.2 bằng ablation study để hiểu model đang học được pattern riêng hay chỉ phụ thuộc vào `rule_based_score`. Phase này chỉ là offline evaluation, không thay production `match_score`, `final_score`, database schema, API contract hoặc frontend.

## Ablation table

| Config | Accuracy | Macro F1 | good -> medium | mismatch -> medium | weak errors |
| --- | ---: | ---: | ---: | ---: | ---: |
| A. Text-only baseline | 0.867 | 0.868 | 0 | 10 | 0 |
| B. Structured không có rule_based_score | 1.000 | 1.000 | 0 | 0 | 0 |
| C. Structured core only | 0.560 | 0.536 | 3 | 5 | 8 |
| D. Full hybrid | 0.947 | 0.947 | 0 | 4 | 0 |

## Feature importance

### A. Text-only baseline

Không có structured feature importance để hiển thị.

### B. Structured không có rule_based_score

| Feature | Importance |
| --- | ---: |
| keyword_score | 0.14157 |
| hybrid_score_candidate | 0.09441 |
| category=same_role_different_stack | 0.08414 |
| confidence | 0.05600 |
| category=cross_domain_transferable | 0.05327 |
| taxonomy_component | 0.04816 |
| skill_score | 0.04586 |
| category=exact_fit | 0.04238 |
| category=role_mismatch | 0.03830 |
| category=strong_evidence | 0.03193 |
| category=keyword_stuffing | 0.02980 |
| role_alignment_score | 0.02719 |
| category=weak_cv | 0.02100 |
| category=career_switch | 0.02060 |
| length_sanity | 0.02027 |
| normalized_skill_overlap_count | 0.02015 |
| category=missing_critical_skill | 0.01900 |
| matched_skill_count | 0.01824 |
| evidence_score | 0.01776 |
| missing_skill_count | 0.01761 |

### C. Structured core only

| Feature | Importance |
| --- | ---: |
| matched_skill_count | 0.24090 |
| role_alignment_score | 0.24065 |
| missing_critical_skill_count | 0.23593 |
| evidence_score | 0.13058 |
| role_family_match | 0.08286 |
| stack_group_match_count | 0.06909 |

### D. Full hybrid

| Feature | Importance |
| --- | ---: |
| keyword_score | 0.03134 |
| hybrid_score_candidate | 0.02086 |
| rule_based_score | 0.02022 |
| category=role_mismatch | 0.01308 |
| confidence | 0.01179 |
| skill_score | 0.01055 |
| category=same_role_different_stack | 0.00973 |
| taxonomy_component | 0.00874 |
| matched_skill_count | 0.00684 |
| evidence_score | 0.00642 |
| category=exact_fit | 0.00634 |
| category=cross_domain_transferable | 0.00589 |
| normalized_skill_overlap_count | 0.00347 |
| role_family_match | 0.00300 |
| missing_skill_count | 0.00292 |
| role_alignment_score | 0.00276 |
| length_sanity | 0.00269 |
| category=strong_evidence | 0.00165 |
| category=career_switch | 0.00136 |
| missing_critical_skill_count | 0.00111 |

## Category error analysis

### A. Text-only baseline

| Category | Errors | Total | Error rate |
| --- | ---: | ---: | ---: |
| career_switch | 0 | 4 | 0.0 |
| cross_domain_transferable | 0 | 8 | 0.0 |
| exact_fit | 0 | 8 | 0.0 |
| keyword_stuffing | 0 | 8 | 0.0 |
| missing_critical_skill | 0 | 8 | 0.0 |
| non_it_mismatch | 0 | 8 | 0.0 |
| role_mismatch | 10 | 11 | 0.909 |
| same_role_different_stack | 0 | 7 | 0.0 |
| strong_evidence | 0 | 7 | 0.0 |
| weak_cv | 0 | 6 | 0.0 |

### B. Structured không có rule_based_score

| Category | Errors | Total | Error rate |
| --- | ---: | ---: | ---: |
| career_switch | 0 | 4 | 0.0 |
| cross_domain_transferable | 0 | 8 | 0.0 |
| exact_fit | 0 | 8 | 0.0 |
| keyword_stuffing | 0 | 8 | 0.0 |
| missing_critical_skill | 0 | 8 | 0.0 |
| non_it_mismatch | 0 | 8 | 0.0 |
| role_mismatch | 0 | 11 | 0.0 |
| same_role_different_stack | 0 | 7 | 0.0 |
| strong_evidence | 0 | 7 | 0.0 |
| weak_cv | 0 | 6 | 0.0 |

### C. Structured core only

| Category | Errors | Total | Error rate |
| --- | ---: | ---: | ---: |
| career_switch | 0 | 4 | 0.0 |
| cross_domain_transferable | 7 | 8 | 0.875 |
| exact_fit | 2 | 8 | 0.25 |
| keyword_stuffing | 5 | 8 | 0.625 |
| missing_critical_skill | 3 | 8 | 0.375 |
| non_it_mismatch | 2 | 8 | 0.25 |
| role_mismatch | 7 | 11 | 0.636 |
| same_role_different_stack | 4 | 7 | 0.571 |
| strong_evidence | 3 | 7 | 0.429 |
| weak_cv | 0 | 6 | 0.0 |

### D. Full hybrid

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

## U01-U10 behavior

### A. Text-only baseline

| Case | Expected | Predicted | Confidence | Agreement |
| --- | --- | --- | ---: | --- |
| U01 | good | weak | 0.630 | major_disagreement |
| U02 | medium | weak | 0.615 | minor_disagreement |
| U03 | good | weak | 0.625 | major_disagreement |
| U04 | weak | weak | 0.615 | aligned |
| U05 | medium | weak | 0.605 | minor_disagreement |
| U06 | weak | weak | 0.625 | aligned |
| U07 | weak | weak | 0.635 | aligned |
| U08 | weak | weak | 0.625 | aligned |
| U09 | weak | weak | 0.625 | aligned |
| U10 | mismatch | weak | 0.605 | minor_disagreement |

### B. Structured không có rule_based_score

| Case | Expected | Predicted | Confidence | Agreement |
| --- | --- | --- | ---: | --- |
| U01 | good | good | 0.845 | aligned |
| U02 | medium | weak | 0.485 | minor_disagreement |
| U03 | good | good | 0.850 | aligned |
| U04 | weak | weak | 0.475 | aligned |
| U05 | medium | weak | 0.520 | minor_disagreement |
| U06 | weak | weak | 0.395 | needs_review |
| U07 | weak | weak | 0.390 | needs_review |
| U08 | weak | medium | 0.360 | needs_review |
| U09 | weak | weak | 0.455 | aligned |
| U10 | mismatch | mismatch | 0.410 | needs_review |

### C. Structured core only

| Case | Expected | Predicted | Confidence | Agreement |
| --- | --- | --- | ---: | --- |
| U01 | good | good | 0.945 | aligned |
| U02 | medium | weak | 0.465 | minor_disagreement |
| U03 | good | good | 1.000 | aligned |
| U04 | weak | mismatch | 0.731 | minor_disagreement |
| U05 | medium | weak | 0.463 | minor_disagreement |
| U06 | weak | mismatch | 0.731 | minor_disagreement |
| U07 | weak | mismatch | 0.506 | minor_disagreement |
| U08 | weak | mismatch | 0.626 | minor_disagreement |
| U09 | weak | mismatch | 0.695 | minor_disagreement |
| U10 | mismatch | mismatch | 0.708 | aligned |

### D. Full hybrid

| Case | Expected | Predicted | Confidence | Agreement |
| --- | --- | --- | ---: | --- |
| U01 | good | weak | 0.645 | major_disagreement |
| U02 | medium | weak | 0.680 | minor_disagreement |
| U03 | good | weak | 0.620 | major_disagreement |
| U04 | weak | weak | 0.695 | aligned |
| U05 | medium | weak | 0.655 | minor_disagreement |
| U06 | weak | weak | 0.675 | aligned |
| U07 | weak | weak | 0.705 | aligned |
| U08 | weak | weak | 0.670 | aligned |
| U09 | weak | weak | 0.705 | aligned |
| U10 | mismatch | weak | 0.715 | minor_disagreement |

## Kết luận

Model vẫn giữ hiệu năng gần full hybrid khi bỏ `rule_based_score`, cho thấy structured component features có tín hiệu riêng đáng giữ.

Cấu hình đáng giữ để tiếp tục đánh giá là `B. Structured không có rule_based_score` và `D. Full hybrid`. `D. Full hybrid` có thể dùng làm upper-bound offline, còn `B` phù hợp hơn để kiểm tra khả năng học độc lập trước khi cân nhắc runtime evaluation.

## Có nên productionize không?

Chưa nên. Kết quả ablation hữu ích để hiểu tín hiệu model, nhưng dataset vẫn là synthetic và benchmark U01-U10 vẫn cần human review. Rule-based matcher tiếp tục là source of truth cho user-facing score.

## Recommendation cho Phase 9.4

1. Chạy ablation tương tự trên real beta cases đã ẩn danh khi có đủ dữ liệu.
2. Thử cấu hình không dùng trực tiếp `rule_based_score` nếu muốn giảm teacher leakage.
3. Bổ sung human-reviewed labels cho nhóm role mismatch và same-role different-stack.
4. Chưa tích hợp hybrid/ML model vào production scoring.
