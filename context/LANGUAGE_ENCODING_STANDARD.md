# Language & Encoding Standard

Date: 2026-06-20

## Định hướng hiện tại

CareerOS AI hiện ưu tiên 100% tiếng Việt cho UI, generated content, docs và reports. Technical terms phổ biến được giữ nguyên khi tự nhiên hơn, ví dụ: Backend, Frontend, Fullstack, REST API, JWT, Docker, FastAPI, Next.js, PostgreSQL, React, TypeScript, Machine Learning và AI.

## Định hướng tương lai

CareerOS AI sẽ hỗ trợ đa ngôn ngữ Việt / Anh thông qua i18n và nút chuyển đổi ngôn ngữ trong một phase riêng. Trước khi có i18n, không triển khai language toggle tạm thời và không trộn tiếng Anh/tiếng Việt nếu không có chủ đích.

## Quy tắc encoding

- File markdown mới phải lưu UTF-8 chuẩn.
- Report mới phải lưu UTF-8 chuẩn.
- Docs mới phải lưu UTF-8 chuẩn.
- Không tạo mojibake như `M?c ti?u`, `Kh?ng thay ??i`, `H??ng d?n`, `Vai tr?`.
- Nếu phát hiện mojibake trong file đang sửa, phải sửa ngay trong cùng phase nếu thuộc scope thay đổi.

## Quy tắc ngôn ngữ

- Generated content mặc định là tiếng Việt tự nhiên.
- UI labels mặc định là tiếng Việt.
- Roadmap, interview feedback, dashboard copy và report phải dùng tiếng Việt làm ngôn ngữ chính.
- Technical terms có thể giữ English khi đó là cách dùng tự nhiên trong ngành.
- Không dùng tiếng Anh làm câu mô tả chính nếu bản tiếng Việt rõ ràng hơn.

## Ghi chú cho future i18n

- Text mới nên được đặt ở vị trí rõ ràng, dễ migrate sang `vi` và `en` sau này.
- Không phân tán text ngôn ngữ lung tung nếu có thể gom vào helper hoặc constants theo domain.
- Chỉ triển khai i18n thật khi có phase riêng, để tránh over-engineer trước khi cần.