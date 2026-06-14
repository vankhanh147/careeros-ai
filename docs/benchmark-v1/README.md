# CareerOS Benchmark V1

CareerOS Benchmark V1 is the internal benchmark set for evaluating Resume <-> JD Matching quality across matcher versions. It is based on the 10 internal beta cases used during Phase 6.3-6.5.

This benchmark is a product-quality guardrail, not a public ML leaderboard and not a hiring-probability model. It exists to keep future matcher changes explainable, deterministic and aligned with real CareerOS AI beta findings.

## Goals

- Preserve strong scores for true exact-fit CV/JD pairs.
- Lower inflated scores for role mismatch and non-IT mismatch cases.
- Keep same-role different-stack cases in a realistic middle range.
- Verify that V2 explanations include role alignment, stack alignment, critical skills, evidence and confidence.
- Prevent future changes from optimizing one case while regressing the broader matcher behavior.

## Files

- `benchmark_cases.md`: the 10 official benchmark cases U01-U10.
- `expected_results_v1.md`: V1 baseline scores and observed issues.
- `expected_results_v2.md`: V2 target ranges and known rerun status.
- `evaluation_notes.md`: manual evaluation rules and release checklist.

## How To Use Before Changing The Matcher

1. Read `context/BETA_REVIEW_V1.md` and this folder.
2. Run the current matcher against the 10 benchmark CV/JD pairs through the UI or API.
3. Record current score, confidence, role families, stack groups, critical skills and notes.
4. Compare scores with `expected_results_v2.md` target ranges.
5. Do not ship a matcher change if exact-fit cases drop too far or mismatch/non-IT cases rise above the target ranges without a clear product reason.

## Non-Goals

- No LLM API.
- No fine-tuning.
- No new AI module.
- No database schema change.
- No automated scoring pipeline required for this phase.
