# Kiến trúc AI

## Tổng quan

CareerOS AI dùng kiến trúc AI nhiều lớp nhưng giữ một ranh giới rõ: **matcher rule-based V2.1 là nguồn điểm production**; taxonomy, semantic, hybrid và ML chủ yếu bổ sung insight hoặc phục vụ evaluation.

```text
CV / JD
  ↓
Trích xuất text + chuẩn hóa kỹ năng
  ↓
Role family / stack / evidence detection
  ↓
Rule-based Matcher V2.1 ─────────────→ match_score production
  │
  ├── Taxonomy insights (read-only)
  ├── Semantic insights (optional, lazy-load)
  ├── Hybrid evaluation candidate
  └── ML evaluation prototype
          ↓
Skill Gap → Resume Feedback → Roadmap → Interview
```

## Lớp matching production

Matcher hiện kết hợp:

- Skill overlap và missing skills.
- Keyword overlap.
- Role-family alignment và role mismatch penalty.
- Stack mismatch penalty.
- Critical skill weighting.
- Evidence-aware scoring dựa trên ngữ cảnh project/experience.
- Length sanity và confidence signal.

Kết quả có breakdown để người dùng và developer hiểu tại sao điểm được hình thành. Fallback rule-based luôn tồn tại, nên hệ thống không phụ thuộc model nặng hoặc dịch vụ bên ngoài.

## Taxonomy và Skill Graph

Career Taxonomy mô tả các nhóm vai trò công nghệ, stack groups và common skills. Skill Graph chuẩn hóa aliases, category và related skills. Hai lớp này hỗ trợ:

- Chuẩn hóa cách gọi kỹ năng.
- Giải thích role family và stack.
- Gợi ý related skills có kiểm soát.
- Giảm trùng lặp giữa matching, roadmap và interview.

Tích hợp hiện là read-only; taxonomy không âm thầm thay đổi score production.

## Semantic và Hybrid Evaluation

Sentence Transformers dùng model nhẹ `all-MiniLM-L6-v2` khi được bật. Model được lazy-load, có thể chạy local và được tắt mặc định trên Render Free. Khi model không khả dụng, analysis tiếp tục bình thường.

Hybrid evaluation kết hợp rule-based, semantic và taxonomy thành một điểm candidate phục vụ so sánh nội bộ. Điểm này không phải source of truth và không thay `final_score`.

## Trainable ML

Các prototype TF-IDF + Logistic Regression và hybrid structured-feature model chứng minh pipeline trainable có thể hoạt động trên synthetic dataset. Ablation study giúp kiểm tra model có học ngoài `rule_based_score` hay chỉ sao chép tín hiệu đã có.

ML prediction hiện là evaluation signal. Không có model candidate nào được tự động đưa vào runtime; registry, review gate, decision record và audit đều khóa `production_safe=false`.

## AI tạo hành động

- **Skill Gap:** ưu tiên missing skills theo role và criticality.
- **Resume Feedback:** template-based, evidence-aware, dùng wording có điều kiện khi thiếu bằng chứng.
- **Roadmap V2:** tạo bài thực hành, CV evidence output và interview prep.
- **Mock Interview V2:** question bank theo role/stack, adaptive ranking và feedback heuristic.

Các module này deterministic, giải thích được và không dùng LLM API.

## Safety boundary

- Không lưu hoặc log toàn bộ CV/JD trong shadow artifacts.
- Không dùng disagreement làm training label trước human review.
- Không tự động approve label, promote dataset hoặc deploy model.
- Không hiển thị score thử nghiệm như điểm chính.
- Không hallucinate kỹ năng, thành tích hoặc khả năng được tuyển.
