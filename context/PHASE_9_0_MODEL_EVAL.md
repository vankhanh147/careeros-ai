# Phase 9.0 Model Evaluation

Date: 2026-06-22T14:01:59.444443+00:00

## Mục tiêu

Đánh giá baseline TF-IDF + Logistic Regression trên Synthetic Dataset V2. Kết quả này chỉ dùng cho evaluation/prototype, chưa thay thế `match_score` production.

## Dataset

- Nguồn dữ liệu: `docs\datasets\synthetic\synthetic_cases.json`
- Tổng số case: 300
- Train size: 225
- Test size: 75
- Random state: 42

## Metrics

- Accuracy: 0.733

## Classification Report

```text
              precision    recall  f1-score   support

        good       0.88      0.47      0.61        15
      medium       0.42      0.93      0.58        15
    mismatch       1.00      0.52      0.69        23
        weak       1.00      1.00      1.00        22

    accuracy                           0.73        75
   macro avg       0.82      0.73      0.72        75
weighted avg       0.86      0.73      0.74        75

```

## Confusion Matrix

| Actual \ Predicted | good | medium | mismatch | weak |
|---|---|---|---|---|
| good | 7 | 8 | 0 | 0 |
| medium | 1 | 14 | 0 | 0 |
| mismatch | 0 | 11 | 12 | 0 |
| weak | 0 | 0 | 0 | 22 |

## Ghi chú

- Dataset là synthetic, không phải dữ liệu beta thật.
- Model chưa được dùng làm điểm chính.
- Cần kiểm chứng thêm bằng benchmark U01-U10 và nhãn người thật trước khi cân nhắc production.
