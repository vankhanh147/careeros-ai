# Ablation Results V1

Date: 2026-06-26T04:25:27.692430+00:00

## Scope

Kết quả ablation offline trên `docs/datasets/synthetic/hybrid_training_dataset.json`. Script không overwrite artifact model hiện có và không thay production scoring.

## Summary

| Config | Accuracy | Macro F1 | good -> medium | mismatch -> medium | weak errors |
| --- | ---: | ---: | ---: | ---: | ---: |
| A. Text-only baseline | 0.867 | 0.868 | 0 | 10 | 0 |
| B. Structured không có rule_based_score | 1.000 | 1.000 | 0 | 0 | 0 |
| C. Structured core only | 0.560 | 0.536 | 3 | 5 | 8 |
| D. Full hybrid | 0.947 | 0.947 | 0 | 4 | 0 |

## Ghi chú

- `D. Full hybrid` là cấu hình gần nhất với Phase 9.2 hybrid model.
- `B. Structured không có rule_based_score` giúp kiểm tra model còn học được gì khi bỏ teacher score trực tiếp.
- `C. Structured core only` kiểm tra nhóm feature tối thiểu về role/evidence/skill count.
- Không cấu hình nào trong file này được dùng làm production score.
