# ML Error Analysis V1

Date: 2026-06-22

## Scope

Phân tích lỗi của `matching_model_v1` trên test split deterministic của Synthetic Dataset V2. Script không train lại model, chỉ dùng artifact hiện có trong `backend/models/`.

## Confusion summary

| Actual -> Predicted | Count |
| --- | ---: |
| good->good | 7 |
| good->medium | 8 |
| medium->good | 1 |
| medium->medium | 14 |
| mismatch->medium | 11 |
| mismatch->mismatch | 12 |
| weak->weak | 22 |

## Key errors

- `good -> medium`: 8
- `mismatch -> medium`: 11
- `medium -> good`: 1
- `medium -> weak`: 0
- `medium -> mismatch`: 0

## Disagreement samples

| Case | Category | Actual | Predicted | Confidence |
| --- | --- | --- | --- | ---: |
| SYN019 | exact_fit | good | medium | 0.392 |
| SYN011 | exact_fit | good | medium | 0.338 |
| SYN118 | role_mismatch | mismatch | medium | 0.433 |
| SYN008 | exact_fit | good | medium | 0.381 |
| SYN105 | role_mismatch | mismatch | medium | 0.473 |
| SYN024 | exact_fit | good | medium | 0.353 |
| SYN117 | role_mismatch | mismatch | medium | 0.475 |
| SYN113 | role_mismatch | mismatch | medium | 0.446 |
| SYN029 | exact_fit | good | medium | 0.407 |
| SYN097 | role_mismatch | mismatch | medium | 0.353 |
| SYN015 | exact_fit | good | medium | 0.326 |
| SYN093 | role_mismatch | mismatch | medium | 0.423 |
| SYN126 | cross_domain_transferable | medium | good | 0.356 |
| SYN099 | role_mismatch | mismatch | medium | 0.382 |
| SYN102 | role_mismatch | mismatch | medium | 0.448 |
| SYN095 | role_mismatch | mismatch | medium | 0.479 |
| SYN021 | exact_fit | good | medium | 0.377 |
| SYN091 | role_mismatch | mismatch | medium | 0.423 |
| SYN023 | exact_fit | good | medium | 0.397 |
| SYN104 | role_mismatch | mismatch | medium | 0.374 |

## Ghi chú

ML V1 còn thiên về nhãn `medium` ở một số boundary case. Đây là tín hiệu cần cải thiện dataset và label review, chưa phải lý do để thay production scoring.
