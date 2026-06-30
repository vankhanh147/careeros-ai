# Roadmap tiếp theo

## Nguyên tắc ưu tiên

Roadmap sau milestone này nên tối ưu cho **độ tin cậy và product signal**, không tối ưu cho số lượng feature. Nền tảng kỹ thuật đã đi trước dữ liệu thực; bước hợp lý là làm đầy khoảng trống bằng beta evidence.

## Ưu tiên ngay: Real beta evidence

### Mục tiêu

Đưa người dùng beta thật qua toàn bộ learning loop và thu dữ liệu có consent: usefulness, disagreement, CV update, analysis rerun và interview completion.

### Điều kiện hoàn thành

- Có tập beta cases đã ẩn danh và human review.
- Có định nghĩa rõ “useful”, “disagreement” và outcome gần hạn.
- Có bằng chứng funnel/retention đủ để biết user kẹt ở bước nào.
- Không đưa raw CV/JD vào training artifact.

### Vì sao đứng đầu

Synthetic dataset và pipeline đã đủ cho prototype. Thêm model trước dữ liệu thật sẽ chủ yếu tối ưu trên pattern do hệ thống tự tạo.

## Tiếp theo: Candidate evidence và offline shadow

### Mục tiêu

Promote dataset version mới có beta labels, train qua Training Job Contract, đưa model qua registry review, benchmark, decision record và release audit.

### Điều kiện hoàn thành

- Candidate cải thiện trên benchmark và beta holdout, không chỉ synthetic split.
- Disagreement queue có human resolution.
- Không làm suy giảm exact fit, same-role/different-stack hoặc non-IT mismatch.
- Candidate vẫn `production_safe=false` cho đến khi có quyết định riêng.

## Sau đó: Controlled learning loop

### Mục tiêu

Dùng case disagreement đã review để cải thiện taxonomy, feature hoặc model theo chu kỳ versioned. Đây là continuous learning có kiểm soát, không phải auto-training.

### Điều kiện hoàn thành

- Label QA và dataset promotion được vận hành thực tế.
- Có reviewer ownership và audit trail.
- Có metric drift/data-quality tối thiểu.

## Khi đủ bằng chứng: Runtime shadow giới hạn

Runtime shadow chỉ nên được cân nhắc khi candidate vượt audit offline, latency budget phù hợp và privacy review hoàn tất. Production score vẫn phải rule-based trong giai đoạn đầu; shadow output không hiển thị cho user và không lưu raw text.

## Hướng nghiên cứu sau: Outcome prediction

Nghiên cứu callback/interview outcome chỉ bắt đầu khi:

- Có consent rõ.
- Label outcome đủ sạch và không tạo bias bất công.
- Có cách giải thích và phản biện prediction.
- Product không biến score thành quyết định tuyển dụng tự động.

## Nên trì hoãn

- Microservices, queue orchestration, Kubernetes và vector database.
- Fine-tuning transformer hoặc LLM workflow.
- Recruiter dashboard lớn, payment và enterprise analytics.
- Gamification, notification system và productivity suite.
- Multilingual i18n trước khi tiếng Việt beta flow ổn định.

## Trật tự đề xuất

```text
Beta thật
→ Nhãn đã review
→ Dataset version mới
→ Candidate offline
→ Shadow offline
→ Runtime shadow giới hạn
→ Quyết định production riêng biệt
```

Đây là con đường ngắn nhất để tăng độ tin cậy mà không đánh đổi sự đơn giản của MVP.
