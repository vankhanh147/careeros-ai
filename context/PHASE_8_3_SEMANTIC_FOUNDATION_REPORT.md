# Phase 8.3 - Semantic Matching Foundation

Date: 2026-06-20

## Mục tiêu

Phase 8.3 bổ sung nền tảng semantic matching bằng embedding theo chế độ parallel/evaluation mode. Mục tiêu là tạo thêm tín hiệu đánh giá ngữ nghĩa cho Resume ↔ JD Matching mà không thay database schema, không đổi API contract cũ, không thay scoring production hiện tại và không làm thay đổi benchmark baseline.

## Kiến trúc semantic

Đã thêm module:

- `backend/app/ai/semantic_matcher.py`

Module này chịu trách nhiệm:

- đọc cấu hình semantic từ environment variables.
- lazy-load Sentence Transformers khi thật sự cần.
- không import `sentence_transformers` nếu `SENTENCE_TRANSFORMERS_ENABLED=false`.
- tính `resume_jd_similarity` cho CV text và JD text khi model khả dụng.
- trả về metadata semantic an toàn khi disabled, text quá ngắn hoặc model load fail.

Response analysis có thêm field additive:

```json
{
  "semantic_insights": {
    "enabled": false,
    "model_name": "all-MiniLM-L6-v2",
    "resume_jd_similarity": null,
    "confidence": "low",
    "notes": ["Semantic matching đang tắt; kết quả hiện dùng rule-based scoring và taxonomy metadata."],
    "reason": "semantic model disabled"
  }
}
```

Field này là metadata song song. Frontend cũ vẫn tương thích vì API contract cũ không bị thay đổi.

## Hành vi env

Các env chính:

- `SENTENCE_TRANSFORMERS_ENABLED=false`
- `SENTENCE_TRANSFORMERS_MODEL_NAME=all-MiniLM-L6-v2`
- `SENTENCE_TRANSFORMERS_LOCAL_FILES_ONLY=true`

Mặc định production/free-tier vẫn tắt semantic model để tránh Render port scan timeout và tránh import torch/sentence-transformers khi app khởi động.

Khi cần test local:

1. Cài đủ dependency trong backend virtualenv.
2. Đảm bảo model đã có local cache hoặc cho phép tải model có chủ đích.
3. Set `SENTENCE_TRANSFORMERS_ENABLED=true`.
4. Set `SENTENCE_TRANSFORMERS_MODEL_NAME=all-MiniLM-L6-v2` hoặc model nhẹ tương đương.
5. Chạy analysis và xem `semantic_insights` trong response hoặc block debug trên `/analysis`.

## Vì sao parallel mode

CareerOS AI hiện đang có matcher deterministic V2.1 đã được benchmark bằng U01-U10. Vì vậy Phase 8.3 không dùng semantic để thay `final_score` ngay.

Lý do:

- tránh làm xấu benchmark baseline khi chưa có raw beta artifacts đầy đủ.
- tránh hành vi khác nhau quá lớn giữa local semantic enabled và Render Free semantic disabled.
- cho phép founder/dev quan sát semantic signal trước khi quyết định Hybrid Matching V3.
- giữ matcher explainable, deterministic và fallback an toàn.

## Frontend

Trang `/analysis` hiển thị block nhỏ `Tín hiệu semantic` trong khu vực debug:

- trạng thái bật/tắt.
- model đang dùng.
- similarity nếu có.
- confidence.
- ghi chú hoặc reason nếu semantic disabled/load fail.

Block này không thay đổi flow chính và không làm người dùng hiểu nhầm rằng semantic đang quyết định điểm cuối cùng.

## Benchmark helper

Đã thêm ackend/scripts/run_semantic_benchmark_notes.py.

Script này không gọi API hoặc database. Khi semantic disabled, script chỉ in trạng thái skipped. Khi dev chủ động bật SENTENCE_TRANSFORMERS_ENABLED=true và model load được, script có thể in similarity tham khảo cho U01-U10 canonical notes. Đây chưa phải benchmark automation chính thức vì repo chưa có raw anonymized CV/JD artifacts.

## Tests đã thêm

Thêm `backend/tests/test_semantic_matching.py`:

- semantic disabled fallback không import `sentence_transformers`.
- model load failure fallback an toàn.
- analysis response có `semantic_insights`.
- metadata semantic song song không thay đổi `final_score`.

## Benchmark safety

Phase 8.3 không cập nhật benchmark baseline. Với default `SENTENCE_TRANSFORMERS_ENABLED=false`, scoring path vẫn giống production Render Free. Semantic metadata được thêm song song và không đi vào `match_score` hoặc `final_score` trong phase này.

## Giới hạn hiện tại

- Chưa có vector database.
- Chưa lưu embedding vào database.
- Chưa có benchmark automation chạy model thật trên U01-U10.
- Chưa tách semantic cho từng section như project/requirement nếu thiếu parser ổn định.
- Khi enabled, semantic vẫn phụ thuộc tài nguyên máy và model cache local.

## Recommendation trước Phase 8.4

Phase 8.4 Hybrid Matching V3 chỉ nên dùng semantic vào scoring thật sau khi:

- có bộ benchmark automation hoặc raw anonymized benchmark artifacts.
- đo được semantic enabled/disabled khác nhau ra sao trên U01-U10.
- xác định weight nhỏ, có cap và fallback rõ ràng.
- giữ `final_score` ổn định giữa production và local/dev hoặc document khác biệt rất rõ.