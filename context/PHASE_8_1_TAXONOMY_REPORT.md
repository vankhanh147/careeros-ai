# Phase 8.1 - Career Taxonomy & Skill Graph Foundation

Date: 2026-06-19

## Mục tiêu

Xây dựng foundation dữ liệu cho AI Intelligence phase tiếp theo mà không thay đổi database schema, API contract, UI hoặc matcher logic production hiện tại.

## Đã thêm

### Role Taxonomy

File: `backend/app/ai/role_taxonomy.py`

Bao gồm 10 nhóm role:

- Backend Developer
- Frontend Developer
- Fullstack Developer
- Mobile Developer
- AI / Machine Learning
- Data Analyst
- Data Engineer
- DevOps
- QA / Testing
- Cybersecurity

Mỗi role có:

- `role_family`
- `stack_groups`
- `common_skills`

### Skill Graph

File: `backend/app/ai/skill_graph.py`

Mỗi skill node có:

- `aliases`
- `category`
- `related_skills`

Các nhóm đã cover nền tảng: authentication/security, frontend, backend, database, DevOps, mobile, AI/ML, data analysis, testing và cybersecurity.

### Documentation

Thêm thư mục `docs/ai-taxonomy/` gồm:

- `README.md`
- `role_taxonomy.md`
- `skill_graph.md`

## Không thay đổi

- Không đổi database schema.
- Không đổi API contract.
- Không đổi UI.
- Không import taxonomy vào matcher hiện tại.
- Không thay đổi scoring production.

## Cách dùng trong Phase sau

Phase 8.2/8.3 có thể dùng taxonomy để:

- Chuẩn hóa role detection giữa matcher, roadmap và interview.
- Normalize skill aliases trước khi scoring.
- Đề xuất related skills có kiểm soát thay vì heuristic rời rạc.
- Giảm duplication giữa `resume_job_matcher.py`, `roadmap_generator.py` và `interview_generator.py`.

## Rủi ro / giới hạn

- Taxonomy hiện là static dictionary, chưa có versioning hoặc admin editing.
- Skill graph chưa phải ontology đầy đủ; chỉ đủ làm foundation MVP.
- Vì chưa tích hợp vào production matcher, phase này không làm thay đổi chất lượng matching ngay lập tức.

## Recommendation

Phase 8.2 nên tích hợp taxonomy theo hướng đọc-only và so sánh song song trước, tránh thay scoring trực tiếp. Sau khi benchmark ổn, mới migrate từng phần khỏi các dictionary cũ trong matcher/interview/roadmap.