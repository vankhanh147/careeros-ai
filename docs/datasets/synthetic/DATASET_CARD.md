# Dataset Card - CareerOS AI Synthetic Dataset V1

Date: 2026-06-21

## Dataset purpose

Synthetic Dataset V1 hỗ trợ CareerOS AI đánh giá các hành vi Resume ↔ JD Matching trước khi có đủ real beta data đã ẩn danh.

Dataset này dùng để kiểm tra các pattern:

- exact fit;
- same-role different-stack;
- role mismatch;
- cross-domain transferable;
- weak CV;
- keyword stuffing;
- non-IT mismatch.

## Source

Dataset được tạo nội bộ bằng script deterministic:

- `backend/scripts/generate_synthetic_dataset.py`

Dataset không lấy từ CV thật, JD thật, website tuyển dụng hoặc dữ liệu cá nhân.

## Synthetic generation method

Script dùng các role/stack template đã định nghĩa sẵn, sau đó sinh case theo nhóm matching.

Mỗi case chứa:

- summary ứng viên;
- summary CV;
- summary JD synthetic;
- target role;
- role family;
- candidate stack;
- JD stack;
- fit label;
- expected score range;
- lý do label;
- skill overlap;
- missing critical skills.

## Intended use

Dataset này phù hợp để:

- kiểm tra validator và tooling dataset;
- bổ sung review thủ công cho matcher;
- tạo guardrail sơ bộ cho Trainable Matching Model sau này;
- phát hiện các hành vi matcher dễ over-score như keyword stuffing hoặc role mismatch.

## Not intended use

Dataset này không nên dùng để:

- train model production một mình;
- thay thế real beta data;
- đánh giá xác suất ứng viên được tuyển;
- thay đổi production `match_score` hoặc `final_score` trực tiếp;
- làm benchmark công khai.

## Label meaning

`fit_label` có 4 giá trị:

- `good`: CV/JD phù hợp mạnh, thường cùng role và stack.
- `medium`: có overlap hoặc transferable skills nhưng vẫn có gap rõ.
- `weak`: có tín hiệu liên quan nhưng evidence yếu hoặc quá generic.
- `mismatch`: role/stack/profile lệch đáng kể so với JD.

`expected_score_range` là khoảng điểm thiết kế để review matcher, không phải nhãn được xác nhận bởi user thật.

## Privacy policy

Dataset không chứa:

- email;
- số điện thoại;
- tên thật;
- raw CV;
- raw JD dài;
- link cá nhân;
- thông tin nhận dạng user.

Validator `backend/scripts/validate_synthetic_dataset.py` kiểm tra các dấu hiệu PII cơ bản trước khi dùng dataset.

## Known limitations

- Case còn dựa trên template nên wording có thể lặp.
- Resume/JD chỉ là summary, chưa phải full artifact.
- Không phản ánh đầy đủ độ nhiễu trong CV thật.
- Không có human feedback từ user thật.
- Một số role family như DevOps, QA và Cybersecurity chưa có coverage sâu trong dataset V1.

## Known biases

- Dataset ưu tiên các role công nghệ phổ biến trong CareerOS AI hiện tại.
- Backend/frontend/AI/mobile/data có coverage nhiều hơn QA, DevOps và Cybersecurity.
- Các label được thiết kế theo kỳ vọng product, không phải kết quả thị trường tuyển dụng.

## Recommendation

Chỉ dùng Synthetic Dataset V1 như một nguồn QA bổ sung. Trước Phase 9.0, cần kết hợp với real anonymized beta dataset và human-reviewed disagreement labels.
