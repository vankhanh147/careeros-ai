# ML Pipeline

## Mục tiêu

ML pipeline của CareerOS AI được thiết kế để tạo bằng chứng trước khi tạo ảnh hưởng production. Mỗi bước để lại metadata truy vết, có validation gate và không tự động vượt qua quyết định của con người.

## Luồng end-to-end

```text
Synthetic + Benchmark + Beta đã review
                    ↓
           Dataset Assembly
          (manifest + SHA256)
                    ↓
             Training Job
                    ↓
       Experiment + Evaluation
                    ↓
           Registry Draft
                    ↓
         Model Review Gate
                    ↓
              Candidate
                    ↓
   Comparison + Deployment Decision
                    ↓
       Release Checklist + Audit
                    ↓
       Offline Shadow Evaluation
                    ↓
 Disagreement Queue → Human Resolution
                    ↓
 Label QA → Promotion Plan → Dataset version mới
```

## Dataset và training contract

Training job không đọc trực tiếp các nguồn rời rạc. Input chuẩn là `training_dataset_v3.json` cùng manifest có fingerprint SHA256. Contract kiểm tra hash, version, label, encoding và config trước khi train; model version đã tồn tại không được overwrite.

Output dự kiến gồm model artifacts, experiment record, evaluation report và registry draft. Tất cả giữ `production_safe=false`.

## Registry và review gate

Train xong không đồng nghĩa candidate. Review gate kiểm tra artifact, dataset version/hash, feature version, experiment, evaluation, benchmark evidence và metric threshold. Kết quả có thể PASS, WARNING hoặc FAIL; write mode chỉ chuyển registry tới `candidate` hoặc `rejected`, không có đường tự động tới production.

## Deployment decision và audit

Candidate được so sánh với baseline `rule_based_matcher_v2.1`. Decision record ghi bằng chứng, risk, rationale và follow-up; `production_change_allowed` luôn false trong pipeline hiện tại.

Release audit kiểm tra dataset, training, model review, quality và governance. “Release Ready offline” chỉ có nghĩa quy trình đủ bằng chứng để xem xét, không có nghĩa model được deploy.

## Offline shadow và human review

Shadow harness so sánh rule, hybrid và candidate trên dataset offline. Nếu chưa có candidate hợp lệ, hệ thống chạy baseline-only và khuyến nghị giữ baseline.

Case bất đồng hoặc confidence thấp được đưa vào review queue không chứa raw text. Item chỉ đi tiếp khi reviewer giải quyết, ghi notes, confidence, anonymization và explicit approval cho Label Review. Draft sau đó vẫn phải qua Label QA và promotion planning; disagreement không bao giờ trở thành training label trực tiếp.

## Trạng thái thực tế

- Pipeline governance và các contract đã có.
- Training dataset v3 có 310 cases.
- Các prototype model V1/hybrid tồn tại cho evaluation.
- Chưa có approved beta case trong training artifact.
- Chưa có candidate được governance pipeline xác nhận để chạy runtime shadow.
- Chưa có production ML inference.

## Vì sao thiết kế này phù hợp

Với startup giai đoạn beta, pipeline file-based và CLI offline giữ chi phí thấp nhưng vẫn tạo discipline về version, traceability và safety. MLflow, feature store hoặc orchestration platform chưa cần thiết khi chưa có tần suất training và quy mô đội ngũ đủ lớn.
