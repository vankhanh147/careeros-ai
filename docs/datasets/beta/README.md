# Beta Evaluation Dataset

Thư mục này chứa structure cho các case beta thật đã ẩn danh. Phase 8.5 chỉ tạo nền tảng format, chưa có dữ liệu người dùng thật trong repo.

## Case naming

- Case thật sau benchmark U01-U10 nên bắt đầu từ `U011`.
- Mỗi case dùng một file JSON riêng.
- Không lưu email, tên thật, số điện thoại, CV text đầy đủ hoặc JD text đầy đủ.

## Field tối thiểu

- `case_id`
- `dataset_type`
- `role_family`
- `candidate_stack`
- `target_role`
- `expected_fit`
- `actual_score`
- `confidence`
- `user_feedback`
- `review_notes`
- `disagreement_notes`

## Trạng thái hiện tại

Các file `U011.json`, `U012.json`, `U013.json` hiện là template pending real case. Khi có beta user thật, thay giá trị `null` bằng dữ liệu đã ẩn danh và giữ nguyên format.
