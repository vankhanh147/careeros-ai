# Phase 8.4 - Hybrid Matching V3 Evaluation Mode

Date: 2026-06-21

## Mục tiêu

Phase 8.4 tạo một hybrid matching candidate kết hợp rule-based score hiện tại, taxonomy insights và semantic insights ở chế độ evaluation/parallel mode. Candidate này giúp đội ngũ đánh giá hướng Hybrid Matching V3 mà không thay đổi `match_score`, `final_score`, database schema hoặc benchmark baseline production.

## Kiến trúc hybrid

Đã thêm module:

- `backend/app/ai/hybrid_evaluation.py`

Module này nhận dữ liệu đã có từ analysis:

- `rule_based_score`: điểm production hiện tại.
- `semantic_insights`: metadata semantic từ Phase 8.3.
- `taxonomy_insights`: metadata taxonomy từ Phase 8.2.
- `scoring_breakdown`: confidence và debug breakdown hiện tại.

Output mới trong analysis response:

```json
{
  "hybrid_evaluation": {
    "enabled": false,
    "hybrid_score_candidate": 78.2,
    "rule_based_score": 78.2,
    "semantic_component": null,
    "taxonomy_component": 80.0,
    "confidence_adjustment": 0.0,
    "explanation_notes": ["Hybrid score candidate chỉ dùng để đánh giá nội bộ, chưa thay thế điểm production."],
    "production_safe": true
  }
}
```

Đây là field additive. API cũ vẫn tương thích.

## Công thức candidate

Khi semantic khả dụng:

```text
hybrid = rule_based_score * 0.70
       + semantic_component * 0.20
       + taxonomy_component * 0.10
       + confidence_adjustment
```

Trong đó:

- `semantic_component` = `resume_jd_similarity * 100`.
- `taxonomy_component` là điểm alignment heuristic từ role family, stack overlap và related skill support.
- `confidence_adjustment` nhỏ: `+2` nếu high confidence, `-5` nếu low confidence, `0` nếu medium.

Khi semantic disabled hoặc load fail:

- `hybrid_score_candidate = rule_based_score`.
- `semantic_component = null`.
- `enabled = false`.
- notes ghi rõ candidate đang mirror rule-based score.

## Vì sao vẫn là evaluation mode

CareerOS AI đang dùng Matching V2.1 làm baseline đã benchmark. Hybrid candidate chưa được dùng làm score chính vì:

- chưa có raw anonymized benchmark artifacts đầy đủ.
- semantic có thể disabled trên Render Free.
- cần quan sát candidate trên U01-U10 và dữ liệu beta thật trước khi thay production score.
- phải tránh làm user hiểu nhầm rằng điểm thử nghiệm đã là nguồn đúng.

## Frontend

Trang `/analysis` hiển thị block nhỏ `Hybrid evaluation (thử nghiệm)` trong phần debug:

- điểm production hiện tại.
- điểm hybrid thử nghiệm.
- semantic đang bật/tắt.
- semantic component.
- taxonomy component.
- ghi chú rõ: điểm này chỉ dùng để đánh giá nội bộ, chưa thay thế điểm chính.

Block này không nổi bật hơn điểm phù hợp chính.

## Benchmark usage

Đã thêm script:

- `backend/scripts/run_hybrid_benchmark_notes.py`

Script không gọi API hoặc database. Nó in checklist U01-U10 gồm:

- `final_score` hiện tại.
- `hybrid_score_candidate`.
- semantic availability.
- notes chính.

Khi semantic disabled, script vẫn chạy và ghi fallback. Khi có raw anonymized artifacts trong tương lai, nội dung CV/JD trong script nên được thay bằng dữ liệu benchmark thật hoặc một runner riêng.

## Tests đã thêm

Thêm `backend/tests/test_hybrid_evaluation.py`:

- analysis response có `hybrid_evaluation`.
- semantic disabled fallback an toàn.
- hybrid metadata không thay đổi `final_score`.
- taxonomy component xử lý được metadata rỗng, không crash.

## Rủi ro / giới hạn

- Hybrid candidate hiện là heuristic, chưa được calibrate bằng dữ liệu thật đầy đủ.
- `taxonomy_component` chỉ là alignment nhẹ, không thay thế role mismatch penalty hiện tại.
- Nếu semantic enabled local nhưng disabled production, candidate có thể khác nhau; vì vậy chưa được dùng làm score chính.
- Chưa có vector database, embedding persistence, fine-tuning hoặc LLM.

## Recommendation trước khi dùng hybrid làm score chính

Trước khi chuyển hybrid thành production scoring:

1. Rerun U01-U10 với raw anonymized benchmark artifacts nếu có.
2. So sánh `final_score` và `hybrid_score_candidate` theo target ranges.
3. Kiểm tra exact-fit không tụt và mismatch không tăng quá mức.
4. Giữ candidate dưới dạng debug/internal ít nhất một vòng beta nữa.
5. Nếu dùng vào production, phải có cap, fallback và release note rõ ràng.