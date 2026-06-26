# Dataset Versioning

## Mục tiêu

Dataset versioning giúp CareerOS AI biết rõ model được train/evaluate từ dữ liệu nào, gồm synthetic cases, benchmark cases và real beta cases đã ẩn danh trong tương lai.

## Metadata chuẩn

Mỗi dataset metadata nên có:

- `dataset_id`
- `version`
- `created_at`
- `source`
- `total_cases`
- `synthetic_cases`
- `benchmark_cases`
- `beta_cases`
- `notes`

## Version hiện tại

`dataset_v2` đang trỏ tới:

```text
docs/datasets/synthetic/synthetic_cases.json
```

Dataset này có 300 synthetic cases và chưa chứa real beta data.

## Quy tắc

- Không lưu PII.
- Không lưu CV/JD thật nếu chưa được ẩn danh và review.
- Không dùng dataset synthetic như bằng chứng production readiness.
- Khi thêm beta data, phải tạo dataset version mới thay vì sửa im lặng version cũ.
