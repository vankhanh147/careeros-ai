# UI_UX_RULES.md

These rules reflect the current frontend implementation after Phase 5.1.

## Product Tone

- CareerOS AI is a real startup/product, not a student demo.
- UI language should be natural, professional Vietnamese.
- Keep technical terms when they are natural and clear: CV, JD, AI, Roadmap, Mock Interview, Resume ↔ JD Matching, Dashboard, API.
- Avoid academic/demo wording.

## Visual Direction

- Current UI uses a dark theme:
  - main background `bg-slate-950`
  - white/slate text
  - cyan accent (`cyan-300`, `cyan-200`)
  - subtle borders `border-white/10`
- Cards use small radius (`rounded-md`/`rounded-lg`) and restrained styling.
- UI should feel like a focused career workspace, not a marketing-only landing page.

## Layout Rules

- Pages should use `overflow-x-hidden` when full-page layouts can contain long text.
- Cards/containers with dynamic content should include `min-w-0`.
- Long file paths, URLs, filenames and generated text must use `break-words`, `break-all`, `truncate`, or constrained overflow as appropriate.
- Desktop can use 2-column layouts for forms/results.
- Mobile/small screens should collapse to 1 column.
- Buttons should stay inside cards and never float into adjacent sections.

## Navigation / CTA Rules

Dashboard cards should provide clear CTAs:

- Hồ sơ nghề nghiệp -> `Cập nhật hồ sơ`
- CV & JD -> `Quản lý CV/JD`
- Resume ↔ JD Matching -> `Phân tích CV ↔ JD`
- Roadmap -> `Tạo roadmap`
- Mock Interview -> `Luyện phỏng vấn`

Empty states should point to the next action instead of only saying data is missing.

## Empty States

Current expected empty states:

- No CV: tell user to upload CV PDF to start matching.
- No JD: tell user to paste/upload JD for matching data.
- No analysis: tell user to choose CV + JD and run matching.
- No roadmap: tell user to generate roadmap from profile or analysis.
- No interview: tell user to start first Mock Interview session.
- Dashboard new user: show recommended next actions from backend.

## Loading States

Use Vietnamese loading messages:

- `Đang tải dashboard...`
- `Đang tải hồ sơ nghề nghiệp...`
- `Đang tải tài liệu...`
- `Đang tải dữ liệu phân tích...`
- `Đang tạo roadmap...`
- `Đang tạo phiên phỏng vấn...`
- `Đang lưu hồ sơ...`
- `Đang upload CV...`
- `Đang đọc JD...`
- `Đang phân tích...`

## Error States

Frontend should show user-friendly Vietnamese errors for:

- Backend connection failure.
- Unauthorized/not logged in.
- Wrong file format.
- File size too large.
- Missing required data such as CV/JD/profile/analysis.
- Save/update/delete failures.

Do not expose raw stack traces to users.

## Label Consistency

Use these labels:

- `Không gian nghề nghiệp`
- `Phân tích gần nhất`
- `Roadmap gần nhất`
- `Phiên phỏng vấn gần nhất`
- `Trạng thái: Đang luyện`
- `Điểm: Chưa hoàn thành`
- `Kỹ năng`
- `Hành động`
- `Kết quả kỳ vọng`
- `Điểm phù hợp`
- `Kỹ năng đã khớp`
- `Kỹ năng còn thiếu`
- `Tóm tắt skill gap`
- `Dữ liệu hệ thống đã đọc được`

## Current Pages

- `/`: dark landing/entry page with primary CTA register and secondary CTA login.
- `/login`: email/password form with Vietnamese error/loading state.
- `/register`: full name/email/password form.
- `/dashboard`: integrated product workspace with cards and latest outputs.
- `/profile`: profile form for career target, level, skills, experience, projects, goal and timeline.
- `/documents`: CV upload, JD upload, paste/edit JD, lists with delete buttons.
- `/analysis`: select CV/JD, run matching, display score/skills/gap/debug/history.
- `/roadmap`: choose analysis/timeline, generate roadmap, display steps and history.
- `/interview`: start interview, answer questions, view feedback, finish session, view history.