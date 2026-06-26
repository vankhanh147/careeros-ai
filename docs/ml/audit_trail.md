# Release Audit Trail

## Mục tiêu

Audit trail giúp CareerOS AI truy vết một model từ dataset, training, registry, review và deployment decision đến kết quả release readiness offline.

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

## Audit lifecycle

1. Đọc manifest và xác minh dataset hash.
2. Đọc training config, experiment, evaluation và model artifacts.
3. Xác minh registry candidate và review PASS.
4. Xác minh deployment decision và risk.
5. Kiểm tra quality evidence, UTF-8, mojibake và PII.
6. Tổng hợp `PASS`, `WARNING`, `FAIL`.
7. Ghi immutable audit record mới trong write mode.

## Schema

Schema nằm tại `backend/ml/configs/audit_record_schema.json`. Audit record gồm reviewer, dataset/model/registry/decision identifiers, toàn bộ checklist, notes và kết quả `passed`.

Mọi record bắt buộc có:

```json
{
  "production_change_allowed": false
}
```

## Chạy dry-run

```bash
python scripts/run_release_audit.py --dry-run
```

Dry-run không ghi file. Nếu chưa có candidate/decision/artifacts, script vẫn in checklist và trả FAIL có giải thích.

Quality command evidence có thể được truyền bằng JSON:

```bash
python scripts/run_release_audit.py --dry-run --quality-evidence path/to/quality.json
```

File evidence có các boolean `pytest`, `compileall`, `pip_check`. Thiếu evidence tạo WARNING, không được tự nhận PASS.

## Write mode

```bash
python scripts/run_release_audit.py --reviewer "founder-review"
```

Audit được ghi tại `backend/ml/audits/{audit_id}.json`. Write mode bắt buộc reviewer và không overwrite audit cũ. Audit FAIL vẫn có thể được ghi để giữ lịch sử trung thực.

## Governance

- Release Ready không đồng nghĩa Production.
- Audit không deploy model.
- Audit không thay `match_score` hoặc `final_score`.
- Audit không cấp quyền runtime inference.
- Mọi runtime/shadow/production change thuộc Phase 11 trở đi.
