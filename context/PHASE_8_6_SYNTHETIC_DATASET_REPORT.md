# Phase 8.6 - Synthetic Dataset Generation Foundation

Date: 2026-06-21

## Mục tiêu

Phase 8.6 tạo synthetic dataset có kiểm soát để chuẩn bị cho trainable matching model trong tương lai, khi CareerOS AI chưa có đủ real beta users.

Phase này không train model, không thay scoring production, không đổi database schema, không thêm LLM API và không thêm vector database.

## Nguyên tắc dữ liệu

- Không scrape CV thật.
- Không lưu CV thật của người khác.
- Không lưu PII.
- Không copy nguyên văn JD dài từ website.
- JD synthetic chỉ dựa trên pattern tuyển dụng phổ biến.
- Dataset được ghi rõ là synthetic, không phải real beta data.
- Synthetic dataset không được dùng một mình để thay production scoring.

## Đã thêm

### Synthetic dataset folder

Tạo thư mục:

- `docs/datasets/synthetic/`

Bên trong gồm:

- `README.md`
- `synthetic_case_schema.json`
- `synthetic_cases.json`

### Dataset ban đầu

Đã tạo 70 synthetic CV/JD matching cases.

Mỗi case có các field chính:

- `case_id`
- `candidate_profile`
- `resume_summary`
- `job_description_summary`
- `target_role`
- `role_family`
- `candidate_stack`
- `jd_stack`
- `fit_label`
- `expected_score_range`
- `reason`
- `skill_overlap`
- `missing_critical_skills`

### Nhóm case

Dataset ban đầu có 7 nhóm, mỗi nhóm 10 case:

- `exact_fit`
- `same_role_different_stack`
- `role_mismatch`
- `cross_domain_transferable`
- `weak_cv`
- `keyword_stuffing`
- `non_it_mismatch`

## Generator script

Đã thêm:

- `backend/scripts/generate_synthetic_dataset.py`

Script deterministic, không gọi external API, không cần database và có thể chạy lại để tái tạo `synthetic_cases.json`.

Cách chạy từ thư mục `backend/`:

```bash
python scripts/generate_synthetic_dataset.py
```

## Test coverage

Đã thêm:

- `backend/tests/test_synthetic_dataset_generator.py`

Test kiểm tra:

- generator tạo đúng 70 cases;
- mỗi nhóm có 10 cases;
- case id chạy từ `SYN001` đến `SYN070`;
- các fit label hợp lệ;
- mỗi case có field tối thiểu theo schema.

## Giới hạn

- Synthetic cases chưa thay thế được real beta data.
- Resume/JD chỉ là summary, chưa phải full anonymized artifacts.
- Expected score range là nhãn thiết kế, chưa phải label được xác nhận bởi user thật.
- Dataset chưa được dùng trong scoring production hoặc training pipeline.

## Recommendation

Phase tiếp theo nên dùng synthetic dataset như một test/evaluation supplement, không dùng làm nguồn truth duy nhất. Trước Phase 9.0, cần kết hợp synthetic cases với real anonymized beta cases và human disagreement review.