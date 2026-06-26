# Label Quality

## Vì sao label quality quan trọng

Trong CareerOS AI, dữ liệu label chất lượng thấp có thể làm model học sai về mức độ phù hợp Resume ↔ JD. Một case có feedback thô kiểu “hữu ích” hoặc “chưa hữu ích” chưa đủ để train model, vì nó không nói rõ user đồng ý với score, label, missing skills hay chỉ thích giao diện hiển thị.

Phase 10.2 đặt label review trước dataset promotion để đảm bảo mỗi case có ngữ cảnh rõ, đã ẩn danh và có human review.

## Khi nào cần human review

Human review là bắt buộc khi:

- Case đến từ beta user thật.
- Rule-based score và human expectation lệch nhau.
- ML/hybrid prediction bất đồng với expected label.
- Case có khả năng gây nhiễu như career switch, keyword stuffing hoặc weak evidence.
- Case được dùng để tạo dataset version mới cho training/evaluation.

## Disagreement workflow

Reviewer nên ghi rõ:

- Human expected label là gì.
- Rule-based/hybrid/ML đang bất đồng ở đâu.
- Bất đồng đến từ role mismatch, stack mismatch, thiếu evidence hay CV/JD quá ngắn.
- Case có nên dùng để training không, hay chỉ dùng để QA benchmark.

## Không train trực tiếp từ feedback thô

Không dùng trực tiếp các signal sau làm training label nếu chưa review:

- Nút “Hữu ích / Chưa hữu ích”.
- Comment ngắn của user không có context.
- Score disagreement chưa được giải thích.
- CV/JD thật chưa ẩn danh.

Feedback thô chỉ là tín hiệu để chọn case cần review. Label training phải đi qua workflow:

```text
Beta feedback → Anonymization → Human review → Approved label → Dataset promotion → Training/evaluation
```

## Nguyên tắc riêng tư

- Không lưu email, số điện thoại, địa chỉ hoặc tên công ty/cá nhân nhạy cảm nếu không cần.
- Không lưu nguyên văn CV/JD thật trong repo.
- Chỉ dùng summary đã ẩn danh và metadata review cần thiết.
- Nếu không chắc một case đã an toàn, giữ `approved_for_training=false`.