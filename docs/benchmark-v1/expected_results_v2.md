# Expected Results V2

V2 target ranges reflect the Phase 6.5 direction: deterministic, explainable matching with role-family detection, stack mismatch penalty, critical skill weighting, evidence-aware scoring and confidence.

These ranges are intentionally broad because CareerOS AI is still MVP-stage. They should be used as regression guardrails, not strict model-training labels.

## Target Ranges By Category

| Category | Acceptable V2 range | Notes |
| --- | ---: | --- |
| Exact fit | 75-90 | Strong role, stack, critical skills and evidence alignment. |
| Strong exact frontend fit | 80-90 | Keep high, but avoid near-perfect scores unless evidence is exceptional. |
| Same role different stack | 50-70 | Preserve transferable role credit while showing stack gap. |
| Role mismatch | 25-50 | Frontend/backend or backend/frontend mismatch should not pass as good fit. |
| Cross-domain transferable | 35-60 | Partial credit for real transferable skills, but clear gap remains. |
| Non-IT mismatch | 10-35 | Non-IT/business profiles should stay low for technical backend/frontend JDs. |

## Per-Case Expected V2 Behavior

| case_id | Category | Target V2 range | Expected V2 behavior | Known V2 score |
| --- | --- | ---: | --- | --- |
| U01 | Exact fit | 75-90 | Score should stay high with backend/.NET evidence and high or medium confidence. | TBD |
| U02 | Same role different stack | 50-70 | Score should drop from V1 because Node.js backend is not .NET backend, but backend transfer remains. | TBD |
| U03 | Strong exact frontend fit | 80-90 | Score should remain high but below V1's 95.8 unless evidence is exceptional. | TBD - exact rerun needed |
| U04 | Role mismatch | 25-50 | Score should drop because React frontend is not .NET backend. | TBD |
| U05 | Cross-domain transferable | 35-60 | Python/backend/AI transfer can count, but missing .NET/C#/ASP.NET should lower final score. | TBD |
| U06 | Role mismatch | 25-50 | Score should drop because .NET backend is not React frontend. | TBD - exact rerun needed |
| U07 | Cross-domain transferable | 35-60 | Flutter/mobile to AI/ML should remain modest unless Python/ML project evidence is present. | TBD |
| U08 | Cross-domain transferable | 35-60 | SQL/data overlap can count but backend engineering gaps should be explicit. | TBD |
| U09 | Role mismatch | 25-50 | Security/frontend mismatch should drop from V1 unless there is real frontend project evidence. | TBD - exact rerun needed |
| U10 | Non-IT mismatch | 10-35 | Business/marketing profile should score low for .NET backend JD. | TBD - possible 52.5 reported, needs verify |

## Improvement Criteria

V2 is considered better than V1 when:

- U01 and U03 remain high enough to feel credible for exact-fit cases.
- U04, U06 and U09 are lower than V1 and land in role-mismatch range.
- U02 remains useful as same-role different-stack, not punished like a total mismatch.
- U10 is clearly lower than V1 or at least flagged as low confidence/poor role alignment if score remains high.
- Explanations show role family, stack groups, critical skills, evidence and confidence clearly.
