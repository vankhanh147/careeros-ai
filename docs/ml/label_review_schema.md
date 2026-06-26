# Label Review Schema

## Mục tiêu

Label review schema chuẩn hóa metadata cho mỗi beta/training case trước khi case được dùng trong dataset promotion hoặc training offline. Schema này giúp CareerOS AI giữ được traceability: biết case đến từ dataset nào, ai đã review, confidence ra sao và case đã đủ an toàn để training chưa.

## Field bắt buộc

| Field | Kiểu dữ liệu | Ý nghĩa |
| --- | --- | --- |
| `case_id` | string | Mã case duy nhất trong review dataset. |
| `dataset_version` | string | Dataset version mà case đang thuộc về hoặc chuẩn bị promote vào. |
| `review_status` | string | Trạng thái review hiện tại. |
| `reviewer` | string | Người hoặc nhóm review nội bộ. Bắt buộc từ `UNDER_REVIEW` trở đi. |
| `review_time` | string | Thời điểm review theo ISO-like timestamp. |
| `label_confidence` | number | Độ tin cậy label, nằm trong khoảng `0..1`. |
| `disagreement_reason` | string | Lý do đồng thuận/bất đồng giữa human label, rule-based score, hybrid hoặc ML signal. |
| `notes` | string | Ghi chú review ngắn, không chứa PII. |
| `approved_for_training` | boolean | Chỉ `true` khi case đủ điều kiện training/evaluation offline. |
| `anonymized` | boolean | Phải `true` trước khi case được approved. |

## Review Status Workflow

```text
NEW
↓
ANONYMIZED
↓
UNDER_REVIEW
↓
APPROVED
↓
PROMOTED
↓
TRAINABLE
```

### NEW

Case vừa được tạo hoặc nhận từ beta feedback thô. Chưa được ẩn danh, chưa được review và chưa được dùng cho training.

### ANONYMIZED

Case đã được loại bỏ PII và text nhạy cảm. Vẫn chưa đủ điều kiện training nếu chưa có review.

### UNDER_REVIEW

Case đang được reviewer kiểm tra label, expected score range, disagreement reason và độ phù hợp với training objective.

### APPROVED

Case đã được human review, đã ẩn danh và có thể dùng cho dataset promotion dạng draft.

### PROMOTED

Case đã được đưa vào một dataset version mới. Trạng thái này chưa đồng nghĩa model đã production-safe.

### TRAINABLE

Case nằm trong dataset version đã được chấp thuận để training/evaluation offline.

## Quy tắc QA

- `review_status` phải thuộc workflow hợp lệ.
- `approved_for_training=true` chỉ hợp lệ với `APPROVED`, `PROMOTED` hoặc `TRAINABLE`.
- `anonymized=true` là bắt buộc trước khi approved.
- `label_confidence` phải nằm trong khoảng `0..1`.
- Không được có email, số điện thoại hoặc PII rõ ràng.
- Không được có mojibake.
- Transition trạng thái chỉ đi theo workflow chuẩn, không nhảy ngược hoặc bỏ qua bước review.

## File JSON schema

Schema máy đọc nằm tại:

```text
backend/ml/configs/label_review_schema.json
```