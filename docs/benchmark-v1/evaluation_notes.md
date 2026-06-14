# Evaluation Notes

## Manual Benchmark Checklist

For each case U01-U10, rerun the current matcher and record:

- final score
- confidence
- CV role family
- JD role family
- CV stack groups
- JD stack groups
- critical skills
- matched skills
- missing skills
- role alignment notes
- evidence notes
- whether the result feels actionable for the user

## Pass Rules

A matcher version is a product improvement if:

- Exact-fit cases stay high.
- Mismatch cases decrease compared with V1.
- Same-role different-stack cases do not collapse too low.
- Non-IT mismatch is lower than V1 or clearly marked low confidence with poor role alignment.
- The explanation is easier to trust than V1.
- Confidence is reasonable for CV/JD length and extraction quality.

## Warning Signs

Investigate before shipping if:

- U01 exact backend fit drops below 70.
- U03 exact frontend fit drops below 75.
- U04, U06 or U09 score above 55.
- U10 scores above 40 without strong real software evidence.
- A score changes dramatically but role/evidence notes do not explain why.
- Semantic disabled/enabled changes score so much that product behavior becomes inconsistent.

## Release Guidance

Before modifying `backend/app/services/resume_job_matcher.py`:

1. Read this benchmark folder and `context/BETA_REVIEW_V1.md`.
2. Rerun all U01-U10 cases manually.
3. Compare against V1 baseline and V2 target ranges.
4. Update `expected_results_v2.md` if exact V2 rerun scores become known.
5. Update `context/AI_SYSTEMS.md` and `context/CHANGELOG.md` if matcher behavior changes.

Do not optimize only for one benchmark case. CareerOS AI needs broadly trustworthy product behavior across fit, partial-fit and mismatch scenarios.
