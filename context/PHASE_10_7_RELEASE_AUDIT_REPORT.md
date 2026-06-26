# Phase 10.7 - Release Readiness Checklist & Audit Trail

Date: 2026-06-27

## Mục tiêu

Phase 10.7 chuẩn hóa Release Readiness Checklist và Audit Trail cho AI Training Infrastructure. Đây là audit offline, không phải deployment và không thay đổi production behavior.

## Workflow

```text
Dataset
↓
Training
↓
Registry
↓
Model Review
↓
Deployment Decision
↓
Release Checklist
↓
Audit Trail
↓
Release Ready offline
```

## Thành phần đã thêm

- `backend/app/ml/release_audit.py`
- `backend/scripts/run_release_audit.py`
- `backend/ml/configs/audit_record_schema.json`
- `backend/ml/audits/`
- `backend/tests/test_release_audit.py`
- `docs/ml/release_readiness.md`
- `docs/ml/audit_trail.md`

## Checklist

Checklist có 21 mục thuộc năm nhóm:

- Dataset
- Training
- Model Review
- Quality
- Governance

Mỗi mục có status `PASS`, `WARNING` hoặc `FAIL`, kèm bằng chứng/nguyên nhân.

## Validation

Audit fail khi thiếu checklist bắt buộc, candidate/review/decision/artifact/evaluation/experiment, dataset hash lệch, có lỗi UTF-8/mojibake/PII hoặc production boundary không hợp lệ.

Quality commands chỉ được PASS khi có evidence rõ. Script không tự khai `pytest`, `compileall` hoặc `pip check` đã đạt.

## Dry-run behavior

Dry-run không ghi file. Với repository hiện tại, audit trả FAIL có kiểm soát vì chưa có training run thật, registry candidate và deployment decision. Dataset manifest/hash vẫn được kiểm tra độc lập.

## Write behavior

Write mode bắt buộc reviewer và ghi audit record mới tại `backend/ml/audits/`. Audit FAIL vẫn được ghi để giữ traceability; file cũ không bị overwrite.

## Production boundary

- `production_change_allowed=false` là bắt buộc.
- Release Ready offline không đồng nghĩa Production.
- Không deploy, shadow deployment hoặc runtime inference.
- Không thay production scoring, `match_score`, `final_score`, database schema, API hoặc UI.

## Giới hạn

- Chưa có candidate thật trong repository.
- Chưa có approved real beta labels.
- Quality evidence hiện là JSON input thủ công, chưa có CI attestation.
- Audit records là JSON local, chưa có chữ ký số hoặc external immutable storage.

## Recommendation Phase 11.0

Chỉ bắt đầu Phase 11 khi có candidate thật vượt review/audit. Phase 11.0 nên tập trung vào thiết kế shadow evaluation an toàn và rollback boundary trên tài liệu trước; chưa bật runtime inference nếu chưa có beta evidence đủ mạnh.
