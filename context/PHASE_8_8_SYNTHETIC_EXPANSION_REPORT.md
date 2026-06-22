# Phase 8.8 - Synthetic Dataset Expansion V2

Date: 2026-06-22

## Mục tiêu

Phase 8.8 mở rộng Synthetic Dataset V1 từ 70 cases lên 300 cases để chuẩn bị cho Trainable Matching Model trong tương lai.

Phase này không train model, không thay production scoring, không đổi `match_score`, không đổi `final_score`, không đổi database schema, không thêm LLM API và không thêm vector database.

## Số lượng case

Synthetic Dataset V2 hiện có:

- Total cases: 300
- Case ID: `SYN001` đến `SYN300`
- Dataset type: `synthetic`
- Generator: `backend/scripts/generate_synthetic_dataset.py`
- Output: `docs/datasets/synthetic/synthetic_cases.json`

## Coverage mới

### Seniority

Dataset V2 có coverage cho:

- Intern
- Fresher
- Junior
- Mid-level

Phân phối sau validation:

- Fresher: 76
- Intern: 75
- Junior: 75
- Mid-level: 74

### Roles

Dataset V2 có 11 target roles:

- Backend Developer
- Frontend Developer
- Fullstack Developer
- Mobile Developer
- AI Engineer
- Machine Learning Engineer
- Data Analyst
- Data Engineer
- DevOps Engineer
- QA Engineer
- Cybersecurity Analyst

Role distribution sau validation:

- Backend Developer: 28
- Frontend Developer: 28
- Fullstack Developer: 28
- AI Engineer: 27
- Machine Learning Engineer: 27
- Mobile Developer: 27
- Data Analyst: 27
- Data Engineer: 27
- DevOps Engineer: 27
- QA Engineer: 27
- Cybersecurity Analyst: 27

### Categories

Dataset V2 có 10 categories, mỗi category 30 cases:

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

### Label distribution

- `good`: 60
- `medium`: 60
- `weak`: 90
- `mismatch`: 90

## Files updated

- `backend/scripts/generate_synthetic_dataset.py`
- `backend/scripts/validate_synthetic_dataset.py`
- `backend/tests/test_synthetic_dataset_generator.py`
- `backend/tests/test_synthetic_dataset_validator.py`
- `docs/datasets/synthetic/synthetic_cases.json`
- `docs/datasets/synthetic/STATISTICS.md`
- `docs/datasets/synthetic/README.md`
- `docs/datasets/synthetic/synthetic_case_schema.json`
- `docs/datasets/synthetic/DATASET_CARD.md`

## Validator update

Validator hiện kiểm tra thêm:

- dataset phải có 300 cases;
- case ID tuần tự từ `SYN001` đến `SYN300`;
- đủ 10 categories, mỗi category 30 case;
- đủ 11 target roles;
- role balance không quá lệch;
- đủ 4 seniority levels;
- seniority balance hợp lý;
- không có PII signal;
- không có raw source signal;
- không có mojibake signal.

Kết quả validator Phase 8.8:

- Errors: 0
- Warnings: 0

## Bias còn tồn tại

- Dataset vẫn là synthetic, chưa phản ánh đầy đủ độ nhiễu của CV/JD thật.
- Một số câu mô tả vẫn có cấu trúc templated vì generator deterministic.
- Expected score ranges là product-designed labels, chưa phải labels được xác nhận bởi user thật.
- Career switch cases còn đại diện ở mức summary, chưa có full anonymized artifact.
- Dataset chưa chứa disagreement notes từ beta users thật.

## Recommendation trước Phase 9.0

Không nên train production model chỉ từ Synthetic Dataset V2.

Khuyến nghị trước Phase 9.0:

1. Dùng Synthetic Dataset V2 để test tooling, validator và matcher behavior supplement.
2. Kết hợp với benchmark U01-U10.
3. Thu thập real anonymized beta cases.
4. Gắn human labels cho disagreement cases.
5. Nếu train model, giữ rule-based matcher làm baseline và dùng synthetic data như auxiliary/evaluation data, không phải source of truth duy nhất.