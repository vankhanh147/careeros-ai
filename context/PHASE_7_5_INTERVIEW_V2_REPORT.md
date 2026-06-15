# Phase 7.5 - Mock Interview Question Bank V2

Date: 2026-06-16
Scope: cải thiện chất lượng câu hỏi và feedback của Mock Interview, đồng thời giữ hệ thống deterministic, rule-based và tương thích với schema hiện tại.

Phase này không thêm LLM API, voice/video, fine-tuning, database schema change hoặc breaking API contract.

## 1. Logic Added

Mock Interview V2 mở rộng hệ thống từ question bank chung theo role thành một luồng luyện phỏng vấn thích nghi hơn với dữ liệu hiện có của user.

Mỗi câu hỏi được sinh ra có thể kèm metadata:

- lý do câu hỏi được hỏi
- kỹ năng liên quan
- loại câu hỏi
- gợi ý trả lời tốt hơn
- expected keywords

Các field này được lưu trong JSON payload hiện có của `InterviewAnswer.expected_keywords`, nên không cần database migration. Response vẫn backward-compatible vì `expected_keywords` vẫn được trả về dưới dạng list, còn metadata mới là các field additive.

## 2. Question Bank Groups

Question Bank V2 gồm các nhóm deterministic:

- Backend .NET
- Backend Node.js
- Backend Python/FastAPI
- Frontend React
- AI/Data
- Mobile Flutter
- General software intern

Mỗi nhóm có kết hợp các loại câu hỏi thực tế:

- concept questions
- project evidence questions
- debugging/troubleshooting questions
- tradeoff questions
- behavioral-lite questions

Ví dụ:

- Backend .NET: JWT trong ASP.NET Core Web API, DTO vs Entity, validation/error response, EF Core Include/AsNoTracking, mô tả endpoint từ request đến database.
- Frontend React: controlled/uncontrolled components, loading/error/empty states, REST API service layer, prop drilling, giải thích state của một màn hình đã xây.
- AI/Data: train/test split, precision/recall/F1, xử lý missing data, overfitting, pipeline ML đơn giản.

## 3. Adaptive Selection Behavior

Khi bắt đầu một interview session, backend ưu tiên nguồn câu hỏi theo thứ tự:

1. Missing skills hoặc critical skills từ analysis.
2. Câu hỏi interview prep từ roadmap gần nhất có liên quan.
3. Question bank theo target role, role family và stack context.
4. Fallback câu hỏi General software intern.

Selection vẫn deterministic và giới hạn 5 câu hỏi để phù hợp với MVP usability.

## 4. Feedback V2 Behavior

Feedback hiện phân loại câu trả lời theo các nhóm dễ hiểu:

- `trả lời quá ngắn`
- `thiếu concept`
- `thiếu ví dụ project`
- `thiếu tradeoff`
- `trả lời quá chung`
- `có dấu hiệu hiểu đúng`

Feedback string giải thích:

- điểm tốt
- điểm còn thiếu
- keyword đã nêu
- gợi ý bổ sung

Evaluator không tự bịa project experience. Hệ thống chỉ khuyến khích user thêm ví dụ project khi họ thật sự có trải nghiệm đó.

## 5. Frontend UX

Trang `/interview` hiện hiển thị rõ:

- vai trò đang luyện
- vì sao câu hỏi được hỏi
- kỹ năng liên quan
- expected keywords
- question category
- feedback category
- better answer hint

UI copy ưu tiên tiếng Việt và dùng Unicode-safe source strings để tránh mojibake.

## 6. Known Limitations

- Question selection vẫn là heuristic và template-based.
- Hệ thống chưa parse sâu toàn bộ CV/JD ngoài các tín hiệu analysis hiện có.
- Câu hỏi lấy từ roadmap phụ thuộc vào chất lượng roadmap và việc user đã tạo roadmap gần đây hay chưa.
- Feedback không phải điểm phỏng vấn tuyệt đối; đây là coaching signal ở mức MVP.
- Chưa có voice/video, follow-up questions hoặc conversational memory.

## 7. Next Recommendations

1. Chạy 5-10 beta interview sessions và hỏi user xem câu hỏi có sát JD đã chọn không.
2. Theo dõi category nào user thường trả lời yếu nhất.
3. Chỉ bổ sung question bank chuyên sâu hơn sau khi thấy nhu cầu thật.
4. Chưa nên thêm LLM interview generation cho đến khi chất lượng deterministic V2 được validate.
