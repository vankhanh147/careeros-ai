# CareerOS AI Taxonomy Foundation

Phase 8.1 tạo lớp dữ liệu nền cho AI Intelligence phase tiếp theo. Nội dung trong thư mục này mô tả role taxonomy và skill graph dùng để chuẩn hóa cách CareerOS AI hiểu role, stack và kỹ năng công nghệ.

## Nguyên tắc

- Không thay đổi matcher production hiện tại.
- Không thay đổi API contract.
- Không thay đổi database schema.
- Không thay đổi UI hiện tại.
- Dữ liệu taxonomy chỉ là foundation để Phase 8.2/8.3 có thể dùng lại.

## Files

- `role_taxonomy.md`: mô tả role families, stack groups và common skills.
- `skill_graph.md`: mô tả skill aliases, categories và related skills.

## Code modules

- `backend/app/ai/role_taxonomy.py`
- `backend/app/ai/skill_graph.py`

Hai module này hiện không được import vào matcher, roadmap hoặc interview production logic.