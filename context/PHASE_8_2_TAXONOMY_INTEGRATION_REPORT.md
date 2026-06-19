# Phase 8.2 - Taxonomy Integration (Read-only Mode)

Date: 2026-06-20

## Mục tiêu

Tích hợp Career Taxonomy và Skill Graph vào CareerOS AI theo chế độ read-only để tạo lớp insight song song, không thay đổi database schema, API contract cũ, UI production, scoring production hoặc benchmark baseline hiện tại.

## Thay đổi đã thực hiện

### Skill Alias Normalization

Thêm helper `backend/app/ai/taxonomy_insights.py` để chuẩn hóa skill aliases bằng `skill_graph.py`.

Ví dụ đã hỗ trợ:

- `asp.net core`, `aspnet core`, `aspnetcore` -> `ASP.NET Core`
- `js`, `javascript` -> `JavaScript`
- `ts`, `typescript` -> `TypeScript`

Normalization chỉ tạo view chuẩn hóa, không thay đổi danh sách skill dùng để tính score production trong matcher.

### Taxonomy Insights Layer

`taxonomy_insights.py` cung cấp:

- `normalize_skill_name`
- `normalize_skill_list`
- `build_taxonomy_insight`
- `build_match_taxonomy_insights`
- `expand_related_skills`

Insight gồm:

- `role_family`
- `stack_groups`
- `normalized_skills`
- `related_skill_suggestions`

### Parallel Matching Metadata

Analysis response có thêm field additive:

```json
{
  "taxonomy_insights": {
    "role_family": "frontend",
    "stack_groups": ["react_frontend"],
    "normalized_skills": ["React", "Next.js", "TypeScript"],
    "related_skill_suggestions": ["REST API integration"],
    "resume": {},
    "job_description": {}
  }
}
```

Đây là metadata song song. Frontend hiện tại không cần render field này và API cũ vẫn tương thích.

### Roadmap Support

Roadmap generator đọc taxonomy ở mức nhẹ:

- normalize skill aliases trong skill queue.
- giảm duplicate skill do alias.
- thêm action nhỏ về kỹ năng liên quan nên tham khảo.

Không đổi database schema, không đổi roadmap architecture, không thêm progress/task system mới.

### Interview Support

Interview generator dùng taxonomy để normalize missing/critical skills trước khi chọn câu hỏi.

Ví dụ: `aspnetcore` được chuẩn hóa thành `ASP.NET Core`, sau đó vẫn chọn được câu hỏi Backend .NET phù hợp.

Không đổi database schema, API contract hoặc logic adaptive chính.

## Benchmark Safety

Đã rerun U01-U10 bằng canonical reconstruction vì repo không chứa raw beta CV/JD gốc. Semantic mode disabled để giống production Render Free.

Kết quả kiểm tra chính của Phase 8.2 là so sánh score khi taxonomy metadata bật và khi taxonomy metadata bị monkeypatch tắt trong cùng runtime:

| Case | Score with taxonomy | Score without taxonomy | Delta |
| --- | ---: | ---: | ---: |
| U01 | 77.8 | 77.8 | 0.0 |
| U02 | 57.7 | 57.7 | 0.0 |
| U03 | 81.3 | 81.3 | 0.0 |
| U04 | 33.1 | 33.1 | 0.0 |
| U05 | 58.9 | 58.9 | 0.0 |
| U06 | 28.3 | 28.3 | 0.0 |
| U07 | 32.9 | 32.9 | 0.0 |
| U08 | 24.1 | 24.1 | 0.0 |
| U09 | 35.9 | 35.9 | 0.0 |
| U10 | 13.5 | 13.5 | 0.0 |

Kết luận: taxonomy layer không làm thay đổi production score. Không cập nhật `docs/benchmark-v1/expected_results_v2.md` vì Phase 8.2 không thay benchmark baseline và không có raw beta artifacts gốc.

## Tests đã thêm

Thêm `backend/tests/test_taxonomy_integration.py`:

- Alias normalization dùng skill graph.
- Taxonomy insight detect frontend stack và related skills.
- Analysis response có `taxonomy_insights` nhưng score không đổi.
- Roadmap đọc taxonomy để normalize skill và gợi ý related skills.
- Interview chọn câu hỏi đúng khi missing skill dùng alias.

## Không thay đổi

- Không đổi database schema.
- Không đổi scoring production.
- Không đổi benchmark baseline.
- Không thêm LLM API.
- Không train model.
- Không thay UI production.

## Rủi ro / giới hạn

- Taxonomy role inference vẫn là heuristic, chưa thay thế matcher role detection.
- Related skill suggestions chỉ là hỗ trợ, không phải skill gap chính thức.
- Field `taxonomy_insights` chưa được frontend hiển thị ở Phase 8.2.
- Canonical benchmark reconstruction không thay thế được raw beta artifacts gốc.

## Recommendation

Phase 8.3 nên tiếp tục read-only hoặc parallel-evaluation mode. Chỉ nên dùng taxonomy để thay scoring thật sau khi có benchmark tự động ổn định và thêm real anonymized CV/JD artifacts.