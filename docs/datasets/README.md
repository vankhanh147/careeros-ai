# CareerOS AI Dataset Foundation

Date: 2026-06-21

Thư mục này định nghĩa nền tảng dữ liệu nội bộ cho các phase AI Intelligence tiếp theo. Mục tiêu là chuẩn hóa cách lưu benchmark, beta feedback và nhãn đánh giá để Phase 9.0 có thể tiến tới Trainable Matching Model mà không làm rối sản phẩm hiện tại.

Phase 8.5 chưa train model, chưa thêm vector database, chưa dùng LLM API và chưa thay đổi scoring production.

## Các loại dataset

### Benchmark dataset

Benchmark dataset là bộ case kiểm thử ổn định dùng để chống regression khi thay matcher.

Hiện tại nguồn chính là:

- `docs/benchmark-v1/benchmark_cases.md`
- `docs/benchmark-v1/expected_results_v1.md`
- `docs/benchmark-v1/expected_results_v2.md`
- `docs/benchmark-v1/evaluation_notes.md`

Benchmark dùng cho câu hỏi:

- Matcher có giữ exact-fit case ở mức cao hợp lý không?
- Role mismatch có bị over-score không?
- Non-IT mismatch có bị đánh giá quá cao không?
- Explanation có đủ rõ để founder/dev tin tưởng không?

### Beta dataset

Beta dataset là dữ liệu đã ẩn danh từ user beta thật. Dữ liệu này dùng để hiểu disagreement giữa user và hệ thống, không dùng để suy luận danh tính user.

Nguyên tắc:

- Không lưu email.
- Không lưu CV text đầy đủ.
- Không lưu JD text đầy đủ.
- Chỉ lưu metadata đã ẩn danh, score, confidence, nhãn useful/not useful và ghi chú review.

Ví dụ structure nằm trong:

- `docs/datasets/beta/`

### Future training dataset

Future training dataset là tập dữ liệu có nhãn tốt hơn, có thể dùng cho Phase 9.0 Trainable Matching Model.

Chỉ nên tạo training dataset khi đã có:

- đủ số lượng case beta thật;
- nhãn human review rõ ràng;
- quy tắc anonymization ổn định;
- benchmark regression guardrail;
- quyết định rõ về model training và evaluation.

## Format chuẩn cho evaluation case

```json
{
  "case_id": "U011",
  "dataset_type": "beta",
  "role_family": "backend",
  "candidate_stack": "Node.js",
  "target_role": "Backend .NET Intern",
  "expected_fit": "same_role_different_stack",
  "actual_score": 62.4,
  "confidence": "medium",
  "user_feedback": "not_useful",
  "review_notes": "User cho rằng điểm còn cao vì thiếu C# và ASP.NET Core.",
  "disagreement_notes": "Role family đúng nhưng stack gap cần được giải thích rõ hơn."
}
```

## Format chuẩn cho feedback label

```json
{
  "case_id": "U011",
  "user_agreed": false,
  "user_disagreed": true,
  "reason": "Điểm matching cao hơn cảm nhận thực tế.",
  "expected_score_range": "45-60",
  "reviewer_notes": "Cần kiểm tra critical skill weighting cho ASP.NET Core."
}
```

## Quy tắc an toàn dữ liệu

- Không đưa dữ liệu PII vào docs hoặc JSON dataset.
- Không lưu raw CV/JD nếu chưa có quy trình ẩn danh rõ ràng.
- Không dùng feedback đơn lẻ để thay scoring ngay.
- Dataset chỉ là nguồn học hỏi và review, không phải kết luận tuyệt đối về năng lực ứng viên.

## Cách dùng trước khi đổi matcher

1. Đọc `docs/benchmark-v1/*`.
2. Đọc các case trong `docs/datasets/beta/` nếu đã có dữ liệu thật.
3. So sánh production `match_score`, `hybrid_score_candidate` và feedback label.
4. Chỉ calibrate matcher khi pattern lặp lại trên nhiều case.
5. Cập nhật `context/AI_SYSTEMS.md`, `context/CHANGELOG.md` và report phase tương ứng.
