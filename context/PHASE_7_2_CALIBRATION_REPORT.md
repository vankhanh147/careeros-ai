# Phase 7.2 - Benchmark Rerun & Matching Calibration V2.1

Date: 2026-06-15
Scope: rerun CareerOS Benchmark U01-U10 against the current deterministic matcher, apply small calibration only if needed, and update benchmark documentation.

No new feature, model, API contract, database schema or architecture change was introduced.

## 1. Benchmark Summary

The rerun used canonical benchmark texts derived from `docs/benchmark-v1/benchmark_cases.md` because the repository does not contain the raw beta CV/JD artifacts. Sentence Transformers was disabled to mirror the Render Free production setting.

| Case | Scenario | V1 | V2.1 | Target | Result |
| --- | --- | ---: | ---: | ---: | --- |
| U01 | .NET Backend -> .NET Backend | 72.6 | 81.9 | 75-90 | Pass |
| U02 | Node.js Backend -> .NET Backend | 75.5 | 62.9 | 50-70 | Pass |
| U03 | React Frontend -> React Frontend | 95.8 | 85.7 | 80-90 | Pass |
| U04 | React Frontend -> .NET Backend | 58.7 | 40.1 | 25-50 | Pass |
| U05 | AI/Python Backend -> .NET Backend | 72.6 | 59.4 | 35-60 | Pass |
| U06 | .NET Backend -> React Frontend | 58.7 | 36.9 | 25-50 | Pass |
| U07 | Flutter Mobile -> AI/ML | 60.5 | 39.3 | 35-60 | Pass |
| U08 | Data Analyst -> .NET Backend | 42.5 | 38.6 | 35-60 | Pass |
| U09 | Cybersecurity -> React Frontend | 51.2 | 44.5 | 25-50 | Pass |
| U10 | Marketing/Business -> .NET Backend | 44.2 | 11.7 | 10-35 | Pass |

## 2. Before vs After Calibration

Initial rerun showed a real matcher weakness: negated skill mentions were counted as positive evidence. Examples:

- `no C#`, `no .NET`, `no ASP.NET Core`
- `no React`, `no Next.js`, `no TypeScript`
- `no backend`, `no API implementation`, `no authentication`

This caused U02, U04, U05, U06, U07, U08, U09 and U10 to score higher than they should, especially U10.

After V2.1 calibration:

- U10 dropped to 11.7 and low confidence.
- U04 dropped to 40.1.
- U06 dropped to 36.9.
- U02 stayed in same-role different-stack range at 62.9.
- U01 and U03 exact-fit anchors stayed high.

## 3. Calibration Changes

Changed `backend/app/services/resume_job_matcher.py` only.

Small changes:

1. Added negation-aware skill detection.
   - The matcher ignores skill occurrences inside short negated clauses.
   - Examples: `no C#`, `without Docker`, `kh?ng c? React`.

2. Added negation-aware evidence scoring.
   - Negated skill mentions no longer increase evidence score.

3. Adjusted role-family selection for specialized profiles.
   - If backend evidence is only generic API/auth/data overlap and no strong backend stack signal exists, mobile or ai/data can become the primary role family.
   - This fixed mobile/data benchmark interpretation without adding a new model.

4. Added two regression tests.
   - Negated skills should not inflate a non-IT/business profile.
   - Flutter/mobile profile should be detected as mobile in a cross-domain AI comparison.

## 4. V1 vs V2.1 Comparison

The most important product movement:

- Exact fit: preserved.
- Same-role different-stack: corrected from over-scored to realistic medium.
- Frontend/backend mismatch: reduced substantially.
- Cross-domain transferable: kept useful but modest.
- Non-IT mismatch: fixed from misleading medium score to clearly low.

This is a better product trust profile than V1 because the score now better matches what a user should believe about their readiness.

## 5. Remaining Weak Spots

- U09 still detects frontend-adjacent signals because cybersecurity text can mention JavaScript/authentication/web security. This is acceptable for MVP but should be monitored.
- Canonical benchmark texts are not the same as original raw production CV/JD files. Future benchmark automation should use real anonymized artifacts if available.
- Confidence is still heuristic, not statistically calibrated.
- Semantic similarity remains disabled in production Free Render mode, so V2.1 is mainly rule-based.
- Negation detection is intentionally lightweight and may miss long or complex sentence structures.

## 6. Confidence Level

Current matcher confidence: medium-high for controlled beta.

Reasoning:

- All U01-U10 cases land inside target ranges.
- The score is deterministic and explainable.
- Calibration fixed a concrete false-positive source without adding complexity.
- Remaining issues are known MVP limitations, not release blockers.

## 7. Recommendation Before Phase 7.3

Recommended next phase: improve score interpretation UX and benchmark discipline, not new AI capability.

Before changing matcher again:

1. Run the production smoke test with real uploaded CV/JD files.
2. Collect 5-10 additional beta examples where users disagree with the score.
3. Add anonymized real benchmark artifacts when possible.
4. Keep V2.1 as baseline until there is concrete evidence for another calibration.
