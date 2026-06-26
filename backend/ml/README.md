# ML Workspace

Thư mục này là workspace offline cho AI training infrastructure của CareerOS AI.

## Mục đích

- Lưu metadata dataset version.
- Lưu metadata model registry.
- Lưu experiment tracking dạng JSON.
- Lưu training config.
- Lưu report evaluation offline.

## Ranh giới

- Không chứa production API.
- Không thay production scoring.
- Không thay `match_score` hoặc `final_score`.
- Không dùng làm runtime inference trực tiếp.
- Không lưu CV/JD thật hoặc PII.

## Cấu trúc

```text
backend/ml/
├── configs/
├── datasets/
├── experiments/
├── models/
├── registry/
└── reports/
```
