# Phase 8.7 - Synthetic Dataset Quality Review

Date: 2026-06-21

## Mục tiêu

Phase 8.7 review chất lượng dataset synthetic SYN001-SYN070 trước khi dùng làm nền cho trainable matching model.

Phase này không train model, không thay scoring production, không đổi database schema, không đổi UI, không thêm LLM API, không thêm vector database và không sửa matcher production.

## Validation tooling

Đã thêm:

- `backend/scripts/validate_synthetic_dataset.py`

Validator kiểm tra:

- `case_id` unique;
- đúng 70 cases;
- đủ 7 nhóm, mỗi nhóm 10 case;
- `fit_label` hợp lệ: `good`, `medium`, `weak`, `mismatch`;
- `expected_score_range` hợp lệ;
- `role_family` hợp lệ;
- không có email/số điện thoại giả quá cụ thể;
- không có dấu hiệu raw CV/JD thật hoặc source tuyển dụng thật;
- không có mojibake;
- không có case thiếu `reason`;
- mismatch case không có `missing_critical_skills` rỗng bất hợp lý.

## Validation result

Kết quả chạy:

```bash
python scripts/validate_synthetic_dataset.py
```

Summary:

- Errors: 0
- Warnings: 0
- Case count: 70
- Group count: 7 nhóm, mỗi nhóm 10 case

Phân phối nhóm:

- `exact_fit`: 10
- `same_role_different_stack`: 10
- `role_mismatch`: 10
- `cross_domain_transferable`: 10
- `weak_cv`: 10
- `keyword_stuffing`: 10
- `non_it_mismatch`: 10

Phân phối label:

- `good`: 10
- `medium`: 20
- `weak`: 20
- `mismatch`: 20

Expected score ranges:

- `75-90`
- `50-70`
- `25-50`
- `35-60`
- `35-55`
- `20-45`
- `10-35`

## Dataset health summary

Dataset hiện đủ tốt để dùng làm QA supplement cho matcher và tooling dataset.

Điểm tốt:

- Nhóm case cân bằng.
- Label phân phối hợp lý cho mục tiêu review mismatch/weak cases.
- Không phát hiện PII.
- Không phát hiện mojibake trong file synthetic scope.
- Có reason cho toàn bộ case.
- Mismatch cases có missing critical skills rõ.

## Label quality review

### Case dễ gây nhiễu

- `keyword_stuffing`: cố ý có skill overlap nhưng thiếu evidence. Đây là nhóm hữu ích để kiểm tra matcher có over-score keyword hay không.
- `cross_domain_transferable`: có transferable skills, dễ bị nhầm với fit mạnh nếu matcher không phân biệt role context.
- `weak_cv`: cùng stack nhưng evidence yếu, dễ gây tranh luận giữa score thấp và score trung bình.

### Expected score range

Không có range invalid.

Các range có chủ đích:

- `75-90` cho exact fit.
- `50-70` cho same-role different-stack.
- `35-60` cho cross-domain transferable.
- `35-55` cho weak CV.
- `20-45` cho keyword stuffing.
- `10-35` cho non-IT mismatch.

Không phát hiện range quá hẹp hoặc quá rộng theo validator hiện tại.

### Reason clarity

Không có case thiếu reason. Reason hiện đủ rõ cho QA, nhưng vẫn là template-level explanation, chưa phải human review thực tế.

## Issues found

Không có lỗi blocking.

Các limitation không blocking:

- Wording còn templated vì generator deterministic.
- Resume/JD chỉ là summary, chưa phải full anonymized artifacts.
- DevOps, QA và Cybersecurity chưa có coverage sâu.
- Dataset chưa có user disagreement label thật.
- Synthetic cases có thể quá “sạch” so với CV/JD thật.

## Issues fixed

Không cần cleanup `synthetic_cases.json` ở Phase 8.7 vì validator pass sạch.

Đã bổ sung:

- validator script;
- validator tests;
- dataset card.

## Recommendation trước Phase 8.8 hoặc 9.0

Không nên sang trainable model production chỉ dựa trên Synthetic Dataset V1.

Khuyến nghị:

1. Dùng synthetic dataset để test tooling và matcher behavior supplement.
2. Thu thập real anonymized beta cases vào `docs/datasets/beta/`.
3. Gắn human feedback labels cho disagreement cases.
4. Mở rộng synthetic coverage cho DevOps, QA, Cybersecurity nếu Phase 8.8 tiếp tục data work.
5. Chỉ bắt đầu Phase 9.0 Trainable Matching Model khi có cả synthetic dataset, benchmark U01-U10 và real anonymized beta labels.
