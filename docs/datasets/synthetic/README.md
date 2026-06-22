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
- `synthetic_cases.json`: 300 synthetic cases V2.
- `STATISTICS.md`: phân phối role, label, category và seniority.

## Nhóm case

Dataset V2 bao gồm 10 nhóm:

- `exact_fit`
- `strong_evidence`
- `same_role_different_stack`
- `role_mismatch`
- `cross_domain_transferable`
- `weak_cv`
- `keyword_stuffing`
- `non_it_mismatch`
- `career_switch`
- `missing_critical_skill`

Mỗi nhóm có 30 case để kiểm tra các hành vi matching quan trọng.

## Coverage V2

Dataset V2 bổ sung:

- seniority: Intern, Fresher, Junior, Mid-level;
- roles: Backend, Frontend, Fullstack, Mobile, AI, Machine Learning, Data Analyst, Data Engineer, DevOps, QA và Cybersecurity;
- career switch cases;
- weak evidence cases;
- strong evidence cases với deploy thật, CI/CD hoặc production experience synthetic.

## Cách tạo lại dataset

Chạy từ thư mục `backend/`:

```bash
python scripts/generate_synthetic_dataset.py
```

Script deterministic, không gọi external API và không cần database.
