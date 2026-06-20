# Synthetic Dataset

Thư mục này chứa synthetic dataset có kiểm soát cho CareerOS AI.

Mục tiêu của dataset là chuẩn bị dữ liệu đánh giá cho Phase 9.0 Trainable Matching Model trong bối cảnh chưa có đủ real beta users.

## Nguyên tắc

- Không scrape CV thật.
- Không lưu CV thật của người khác.
- Không lưu PII.
- Không copy nguyên văn JD dài từ website.
- JD synthetic chỉ dựa trên pattern tuyển dụng phổ biến.
- Dataset phải được xem là synthetic, không phải real beta data.
- Không dùng trực tiếp để thay production scoring.

## Files

- `synthetic_case_schema.json`: schema tối thiểu cho một synthetic case.
- `synthetic_cases.json`: 70 synthetic cases ban đầu.

## Nhóm case

Dataset ban đầu bao gồm 7 nhóm:

- `exact_fit`
- `same_role_different_stack`
- `role_mismatch`
- `cross_domain_transferable`
- `weak_cv`
- `keyword_stuffing`
- `non_it_mismatch`

Mỗi nhóm có 10 case để kiểm tra các hành vi matching quan trọng.

## Cách tạo lại dataset

Chạy từ thư mục `backend/`:

```bash
python scripts/generate_synthetic_dataset.py
```

Script deterministic, không gọi external API và không cần database.
