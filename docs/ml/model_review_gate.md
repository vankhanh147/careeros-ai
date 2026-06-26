# Model Registry Review Gate

## Mục tiêu

Model Registry Review Gate là bước kiểm soát giữa registry draft và model candidate. Gate chỉ review metadata, artifacts và bằng chứng evaluation; không train, không inference và không deploy model.

```text
Training Job
↓
Registry Draft
↓
Review Gate
↓
Candidate hoặc Rejected
↓
Deployment Decision trong phase tương lai
```

## Cấu hình

Config nằm tại `backend/ml/configs/model_review_config.json`:

- `registry_path`: registry draft cần review.
- `dataset_manifest_path`: manifest dùng đối chiếu dataset version/hash.
- `minimum_accuracy`: ngưỡng accuracy.
- `minimum_macro_f1`: ngưỡng macro F1.
- `warning_margin`: khoảng dưới ngưỡng được phân loại WARNING thay vì FAIL.
- `benchmark_required`: có bắt buộc bằng chứng benchmark hay không.
- `required_evaluation_fields`: các field metrics bắt buộc.

Ngưỡng là policy offline có thể cấu hình, không được hardcode vào production.

## Review rules

Gate kiểm tra:

- Registry tồn tại và đủ metadata.
- Model artifacts, experiment record và evaluation report tồn tại.
- Dataset version/hash khớp manifest.
- Feature version không rỗng.
- Metrics nằm trong khoảng hợp lệ và đạt ngưỡng cấu hình.
- Evaluation report có đủ field bắt buộc.
- Benchmark result tồn tại nếu policy yêu cầu.
- Không có registry trùng `model_version`.
- `production_safe` luôn là `false`.

## Kết quả

- `PASS`: không có lỗi/cảnh báo; có thể chuyển `candidate`.
- `WARNING`: không có lỗi chặn, nhưng có metrics sát ngưỡng; có thể chuyển `candidate` sau khi người review cân nhắc.
- `FAIL`: có lỗi toàn vẹn hoặc metrics thấp rõ rệt; chuyển `rejected`.

## Registry lifecycle

```text
draft → under_review → candidate
                     ↘ rejected
```

Trạng thái `production` được ghi nhận cho lifecycle tương lai nhưng Phase 10.5 không có code path chuyển sang trạng thái này.

## Chạy review

Dry-run:

```bash
python scripts/review_model_registry.py --dry-run
```

Dry-run in PASS/WARNING/FAIL, lý do và recommendation nhưng không sửa registry.

Write mode:

```bash
python scripts/review_model_registry.py
```

Write mode chỉ cập nhật `candidate` hoặc `rejected`, ghi `review_history` và giữ `production_safe=false`.

## Production boundary

Candidate không đồng nghĩa production. Model vẫn cần deployment decision riêng, benchmark/beta evidence phù hợp và tích hợp runtime trong phase được phê duyệt rõ ràng.
