# Data Pipeline

## Các lớp dữ liệu

CareerOS AI phân biệt rõ ba loại dữ liệu:

1. **Benchmark:** 10 case U01–U10 dùng để phát hiện regression và kiểm tra hành vi matcher ở các tình huống exact fit, khác stack, role mismatch, cross-domain và non-IT mismatch.
2. **Synthetic:** 300 case deterministic, không PII, bao phủ role, seniority, category và label để thử nghiệm feature/training pipeline.
3. **Beta:** cấu trúc dành cho case người dùng thật đã ẩn danh và human review. Training artifact hiện chưa có beta case được approve.

## Trạng thái dataset chuẩn

Dataset assembly hiện tạo `dataset_v3` gồm:

- 300 synthetic cases.
- 10 benchmark cases.
- 0 approved beta cases.
- Tổng cộng 310 cases.
- Fingerprint SHA256 để phát hiện thay đổi artifact.

Phân phối được theo dõi theo role family, category, fit label, seniority và source. Dataset này đủ để kiểm chứng pipeline, nhưng chưa đủ để tuyên bố model đại diện tốt cho hành vi ứng viên thật.

## Vòng đời dữ liệu

```text
Nguồn dữ liệu
    ↓
Kiểm tra schema, label, PII, encoding, duplicate
    ↓
Human review và anonymization đối với beta data
    ↓
Dataset promotion draft
    ↓
Assembly artifact bất biến
    ↓
Manifest + statistics + SHA256
    ↓
Training / Evaluation
```

Dataset version cũ không bị sửa im lặng. Version mới phải có metadata riêng, source traceability và trạng thái draft trước khi được dùng.

## Label quality

Workflow review chuẩn là:

```text
NEW → ANONYMIZED → UNDER_REVIEW → APPROVED → PROMOTED → TRAINABLE
```

`approved_for_training=true` chỉ hợp lệ sau anonymization và ở trạng thái phù hợp. Reviewer, review time, confidence, disagreement reason và notes là các bằng chứng bắt buộc. Feedback thô hoặc disagreement từ shadow không được dùng trực tiếp làm label.

## Privacy boundary

- Không scrape CV thật.
- Không lưu PII không cần thiết.
- Shadow artifacts không lưu raw CV/JD text.
- Dataset validation chặn pattern email, số điện thoại, mojibake và BOM.
- Beta labels phải được ẩn danh trước khi xét promotion.

## Chất lượng và bias

Synthetic data có lợi cho coverage và deterministic testing, nhưng dễ mang bias từ template generation. Các case có thể sạch và cân bằng hơn dữ liệu thật, khiến metric offline lạc quan. Benchmark U01–U10 nhỏ và chủ yếu đo các pattern đã biết.

Do đó, dataset hiện là nền tảng kỹ thuật tốt nhưng chưa phải lợi thế dữ liệu. Lợi thế chỉ hình thành khi CareerOS AI thu được case beta thật, disagreement có review và tín hiệu outcome đủ tin cậy.

## Hướng tiến hóa

Ưu tiên kế tiếp là thu thập beta labels tối thiểu, ẩn danh và có reviewer agreement; sau đó promote thành dataset version mới theo pipeline hiện có. Chỉ khi dữ liệu thật đủ đa dạng mới nên cân nhắc model phức tạp hơn hoặc runtime shadow.
