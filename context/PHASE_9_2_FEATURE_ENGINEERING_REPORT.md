# Phase 9.2 - Feature Engineering & Hybrid Dataset V1

Date: 2026-06-25

## Mục tiêu

Phase 9.2 cải thiện dữ liệu đầu vào cho trainable matching model bằng cách kết hợp text features với structured features từ rule-based matcher, taxonomy, semantic/hybrid metadata và metadata của dataset. Phase này là offline data/feature engineering, không thay production scoring.

## Nhóm feature đã thêm

### Feature từ rule-based matcher

- `rule_based_score`
- `skill_score`
- `keyword_score`
- `role_alignment_score`
- `evidence_score`
- `confidence`
- `length_sanity`
- `critical_skill_count`
- `missing_critical_skill_count`
- `matched_skill_count`
- `missing_skill_count`

### Feature từ taxonomy

- `role_family_match`
- `stack_group_match_count`
- `normalized_skill_overlap_count`
- `related_skill_support_count`

### Feature từ semantic/hybrid metadata

- `semantic_available`
- `semantic_similarity`
- `hybrid_score_candidate`
- `taxonomy_component`
- `confidence_adjustment`

### Feature từ dataset metadata

- `seniority_level`
- `category`
- `target_role`
- `candidate_stack`
- `jd_stack`

## Dataset đã build

Output files:

- `docs/datasets/synthetic/hybrid_training_dataset.json`
- `docs/datasets/synthetic/hybrid_feature_schema.json`

Kích thước dataset:

- Rows: 300
- Source: `docs/datasets/synthetic/synthetic_cases.json`
- Each row includes `case_id`, `text_input`, `structured_features`, `label`, `source_category` and `expected_score_range`.

Validation:

- `python scripts/validate_hybrid_training_dataset.py` passes with 0 errors and 0 warnings.

## Hybrid model

Đã tạo artifact offline riêng:

- `backend/models/hybrid_matching_model.joblib`
- `backend/models/hybrid_matching_vectorizer.joblib`
- `backend/models/hybrid_model_metadata.json`

Model sử dụng:

- TF-IDF text features.
- DictVectorizer structured features.
- RandomForestClassifier baseline.

Text-only artifacts V1 không bị overwrite.

## So sánh metrics

From `context/PHASE_9_2_HYBRID_FEATURE_EVAL.md`:

| Model | Accuracy | Macro F1 | good -> medium | mismatch -> medium | weak errors |
| --- | ---: | ---: | ---: | ---: | ---: |
| Text-only V1 | 0.733 | 0.719 | 8 | 11 | 0 |
| Hybrid feature model | 0.947 | 0.947 | 0 | 4 | 0 |

Diễn giải:

- Hybrid features xử lý được lỗi chính `good -> medium` trên deterministic test split.
- `mismatch -> medium` cải thiện nhưng vẫn còn 4 lỗi, tất cả nằm trong nhóm `role_mismatch`.
- Nhóm `weak` không xấu đi.

## Giới hạn

- Dataset vẫn là synthetic, chưa phải real beta data.
- Hybrid model học nhiều từ tín hiệu rule-based matcher, đặc biệt là `rule_based_score` và role/evidence features.
- Semantic đang disabled trong môi trường hiện tại, nên các semantic fields có mặt nhưng chưa nhiều giá trị thông tin.
- Hiệu năng cao trên synthetic dataset chưa đồng nghĩa với production readiness.
- Phase này chưa thêm runtime integration.

## Recommendation cho Phase 9.3

1. Chạy benchmark U01-U10 với hybrid artifact ở chế độ offline evaluation.
2. Bổ sung human-reviewed labels cho role mismatch và same-role different-stack cases.
3. Đánh giá lại việc có nên đưa trực tiếp `rule_based_score` vào model hay thay bằng component scores ít leakage hơn trước mọi thảo luận production.
4. Giữ rule-based matcher là source of truth cho đến khi hybrid model được validate trên real beta cases đã ẩn danh.
5. Cân nhắc ablation study nhỏ: text-only, structured không có `rule_based_score`, structured với đầy đủ matcher features.
