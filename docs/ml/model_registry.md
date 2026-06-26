# Model Registry

## Mục tiêu

Model registry lưu metadata model artifact dưới dạng JSON để biết model được train từ dataset nào, dùng feature version nào và có metrics ra sao.

## Metadata chuẩn

Mỗi model registry record nên có:

- `model_name`
- `model_version`
- `dataset_version`
- `feature_version`
- `accuracy`
- `macro_f1`
- `created_at`
- `training_command`
- `artifact_paths`
- `production_safe`
- `notes`

## Ranh giới

Registry trong Phase 10.0 chỉ là file JSON local, chưa phải model serving system.

Model có trong registry không đồng nghĩa được dùng làm production score. Mọi quyết định production phải qua benchmark, beta validation và review riêng.

## Registry draft từ Training Job Contract

Từ Phase 10.4, `run_training_job.py` có thể tạo registry draft tại:

- `backend/ml/registry/{model_version}.json`

Registry draft phải có:

- `dataset_hash`
- `artifact_paths`
- `status=draft`
- `production_safe=false`

Nếu `model_version` đã tồn tại, training job phải fail và không overwrite artifact cũ.

## Review gate từ Phase 10.5

Registry lifecycle offline:

```text
draft → under_review → candidate
                     ↘ rejected
```

Review gate đối chiếu artifact, dataset hash, experiment, evaluation report, metrics và benchmark policy trước khi cập nhật trạng thái. `candidate` không đồng nghĩa `production`; Phase 10.5 không có code path chuyển model thành production.

Chi tiết: `docs/ml/model_review_gate.md`.

## Deployment Decision Record từ Phase 10.6

Model có status `candidate` mới được đưa vào comparison workflow. Candidate được so sánh với baseline `rule_based_matcher_v2.1` bằng metrics, benchmark evidence, dataset version/hash, review outcome và known limitations.

Kết quả được ghi thành decision record offline. `approve_candidate` không đồng nghĩa model được deploy hoặc trở thành production.

Chi tiết: `docs/ml/deployment_decision.md`.
