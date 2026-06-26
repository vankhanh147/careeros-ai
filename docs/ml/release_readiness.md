# Release Readiness Checklist

Release Ready trong tài liệu này chỉ có nghĩa quy trình AI offline đã đầy đủ bằng chứng và có thể audit. Nó không đồng nghĩa production-ready và không cấp quyền thay đổi runtime.

## Dataset

- [ ] Dataset version được ghi trong manifest.
- [ ] Dataset hash khớp artifact.
- [ ] Beta labels đã approved và anonymized; nếu chưa có beta labels phải ghi WARNING.
- [ ] Benchmark đã hoàn tất và có trong evaluation report.

## Training

- [ ] Training config tồn tại.
- [ ] Experiment record tồn tại.
- [ ] Evaluation report tồn tại.
- [ ] Model artifact và model metadata tồn tại.

## Model Review

- [ ] Model review có outcome PASS.
- [ ] Registry có status `candidate`.
- [ ] Deployment Decision Record tồn tại và khớp candidate.
- [ ] Risk đã được reviewer chấp nhận.

## Quality

- [ ] `pytest` pass và có evidence.
- [ ] `compileall` pass và có evidence.
- [ ] `pip check` pass và có evidence.
- [ ] File audit liên quan là UTF-8 không BOM.
- [ ] Không có mojibake.
- [ ] Dataset không có PII.

## Governance

- [ ] Registry giữ `production_safe=false`.
- [ ] Deployment decision tồn tại.
- [ ] Audit checklist đã hoàn tất.

## Kết quả

- `PASS`: mọi mục bắt buộc đã đạt.
- `WARNING`: không có lỗi chặn nhưng còn giới hạn cần xử lý.
- `FAIL`: thiếu bằng chứng bắt buộc hoặc vi phạm production boundary.

Checklist đầy đủ có 21 mục và được ghi trong `checklist_result` của audit record.
