# Phase 9.0 - Trainable Matching Model V1

Date: 2026-06-22

## Mục tiêu

Phase 9.0 tạo baseline ML đầu tiên cho CareerOS AI để dự đoán nhãn mức độ phù hợp Resume ↔ JD từ Synthetic Dataset V2. Model này chỉ phục vụ evaluation/prototype và chưa thay thế `match_score` hoặc `scoring_breakdown.final_score` production.

## Model choice

Baseline được chọn:

- TF-IDF cho feature text.
- Logistic Regression cho phân loại.
- Output là `fit_label`: `good`, `medium`, `weak`, `mismatch`.

Lý do chọn:

- Nhẹ, chạy được CPU, không cần GPU.
- Deterministic, dễ debug và phù hợp MVP.
- Không fine-tune transformer.
- Không cần vector database hoặc hạ tầng mới.
- Phù hợp làm baseline trước khi có real beta labels đủ tốt.

## Dataset used

Nguồn train:

- `docs/datasets/synthetic/synthetic_cases.json`
- 300 synthetic cases từ Phase 8.8.
- Không dùng dữ liệu user thật.
- Không chứa PII.

Split:

- Train size: 225
- Test size: 75
- `random_state=42`
- Stratified split theo `fit_label`

Feature input:

- `resume_summary`
- `job_description_summary`
- `target_role`
- `role_family`
- `candidate_stack`
- `jd_stack`
- `missing_critical_skills`
- `skill_overlap`

## Artifacts

Training script tạo artifacts trong `backend/models/`:

- `matching_model.joblib`
- `matching_vectorizer.joblib`
- `label_mapping.json`
- `model_metadata.json`

Runtime predictor nằm ở:

- `backend/app/ml/matching_predictor.py`

Predictor fallback an toàn nếu artifact chưa tồn tại hoặc load lỗi.

## Metrics

Kết quả từ `python scripts/train_matching_model.py`:

- Accuracy: `0.733`

Classification summary:

- `weak`: precision/recall tốt nhất trong test set.
- `good`: precision cao nhưng recall còn thấp, một số case good bị kéo về medium.
- `mismatch`: precision cao nhưng recall còn thấp, một số mismatch bị kéo về medium.
- `medium`: recall cao nhưng precision thấp hơn, cho thấy model còn thiên về nhãn trung gian.

Chi tiết nằm ở:

- `context/PHASE_9_0_MODEL_EVAL.md`

## Runtime integration

Analysis response có field additive mới:

```json
{
  "ml_evaluation": {
    "enabled": true,
    "predicted_label": "medium",
    "confidence": 0.72,
    "label_probabilities": {
      "good": 0.1,
      "medium": 0.72,
      "weak": 0.14,
      "mismatch": 0.04
    },
    "model_version": "matching_model_v1",
    "production_safe": false,
    "note": "ML prediction chỉ dùng để đánh giá nội bộ, chưa thay thế điểm chính."
  }
}
```

Nếu artifact chưa có:

- `enabled=false`
- `reason` giải thích rõ.
- Analysis không crash.
- `match_score` và `final_score` không đổi.

## Frontend

Trang `/analysis` có block nhỏ:

- `ML evaluation (thử nghiệm)`
- nhãn dự đoán
- độ tự tin
- phiên bản model
- ghi chú rằng tín hiệu này chưa thay thế điểm chính

Block này không nổi bật hơn điểm production hiện tại.

## Vì sao chưa dùng production

Model chưa dùng production vì:

- Dataset hiện vẫn là synthetic, chưa đủ real beta labels.
- Chưa có review nhãn người thật cho disagreement cases.
- Model còn xu hướng kéo một số `good` và `mismatch` về `medium`.
- Chưa benchmark trực tiếp với U01-U10 bằng predictor artifact.
- Rule-based matcher hiện vẫn explainable và đáng tin hơn cho user-facing score.

## Recommendation Phase 9.1

Phase 9.1 nên tập trung vào evaluation, không promote model vội:

- Chạy model trên benchmark U01-U10 và so sánh với expected ranges.
- Thu thập anonymized beta labels thật.
- Tạo disagreement review giữa rule-based score, hybrid candidate và ML label.
- Cải thiện dataset balance cho boundary cases good/medium và mismatch/medium.
- Chỉ cân nhắc Hybrid/ML score production sau khi có benchmark ổn định và human-reviewed labels.

