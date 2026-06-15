# Phase 7.4 - Roadmap Quality V2

Date: 2026-06-15
Scope: improve Personalized Roadmap quality with action-oriented roadmap items. No LLM API, no fine-tuning, no database schema change and no breaking API contract.

## 1. Logic Added

Roadmap items now include practical fields in addition to the existing `week`, `focus`, `skills`, `actions` and `expected_output` fields:

- `learning_focus`
- `practice_task`
- `cv_evidence_output`
- `interview_prep`
- `priority`

The generator remains rule-based and deterministic.

## 2. Inputs Used

When generating from analysis, Roadmap V2 uses:

- target role from profile/JD
- timeline
- prioritized missing skills
- improvement plan
- critical skills from scoring breakdown
- confidence from scoring breakdown
- resume feedback hints when available
- JD role family and stack groups when available

When no analysis is selected, roadmap still works from career profile, but the summary clearly says personalization is lower because it is generated from profile only.

## 3. Item Count Rules

The roadmap stays short:

- 1-2 weeks: 1-2 items
- 4 weeks: 4 items
- 6 weeks: 6 items
- 8+ weeks: capped at 6-8 items

The title still reflects the requested timeline, while items stay concise enough for MVP use.

## 4. Example Output

For a Backend .NET user missing JWT/authentication, a roadmap item can include:

- Learning focus: High-priority focus: learn and prove authentication, jwt because it is important for Backend Developer.
- Practice task: Build login/register, one protected endpoint and one role-based authorization check.
- CV evidence output: If you complete this task, you can add: `Implemented authentication/JWT flow for protected API endpoints.`
- Interview prep:
  - How does JWT authentication work?
  - How would you protect an endpoint by role?
- Priority: high

## 5. Safety Rules

Roadmap V2 avoids unsafe claims:

- It does not say the user already has a skill if evidence is missing.
- It uses conditional CV output wording such as `If accurate...` or `If you complete this task...`.
- It does not invent fake metrics or achievements.
- It avoids suggesting too many skills in one item.
- It does not promise hiring outcomes.

## 6. Benchmark/User Scenarios Checked

Tests cover:

- Roadmap generated from career profile still works.
- Roadmap generated from analysis still works.
- Timeline parser still supports 1 week, 2 weeks, 1 month and fallback 6 weeks.
- Roadmap item has practice task.
- Roadmap item has CV evidence output.
- Roadmap item has interview prep.
- Missing critical skills are prioritized.
- Profile-only fallback roadmap clearly indicates lower personalization.

## 7. Limitations

- Roadmap V2 is still heuristic and template-based.
- It does not track completion/progress yet.
- It does not know whether a user actually completed tasks after generation.
- It does not generate long multi-month curricula.
- It relies on analysis quality and extracted CV/JD text quality.
- Existing roadmap history items generated before Phase 7.4 may not have all V2 fields, but schema/frontend handle optional fields safely.

## 8. Recommendation Before Next Phase

Recommended next phase: beta test Roadmap V2 with 5-10 users and ask whether each item answers three questions:

1. What should I do this week?
2. What evidence can I add to my CV after doing it?
3. What interview question should I be ready to answer?

Do not add progress tracking or LLM roadmap generation until this action-plan format is validated with real users.
