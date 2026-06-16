# Phase 7.7 - Lightweight Founder Insights

Date: 2026-06-16

## Goal

Phase 7.7 gives the founder a lightweight view of how beta users move through CareerOS AI, without turning the product into an analytics platform.

The implementation reuses existing `UsageEvent`, `UserFeedback` and product tables. No Mixpanel, PostHog, chart library, new event system, admin dashboard or database schema change was added.

## Metrics Added

### Product Funnel

The founder can now see aggregate user counts for:

- registered users
- profile completed users
- users with uploaded CV
- users with saved/uploaded JD
- users who generated analysis
- users who generated roadmap
- users who started interview
- users who completed interview

### Feedback Summary

Feedback is aggregated by type:

- analysis
- roadmap
- interview

Each type shows total feedback, useful count, not useful count and useful rate.

### Common Missing Skills

Top missing skills are counted from stored `MatchAnalysis.missing_skills` JSON. This is intentionally simple and does not run NLP over CV/JD text.

### Average Matching Health

Founder insights show:

- total analyses
- average match score
- high / medium / low / unknown confidence cases

Confidence is recomputed from existing analysis resume/JD text using the current deterministic matcher, but raw CV/JD text is never returned.

### Learning Loop Signal

Founder insights show:

- users completing roadmap items
- completed roadmap items total
- users rerunning analysis after roadmap

The rerun signal is inferred from existing analysis and roadmap records. It is a directional product signal, not a full event analytics system.

## Access Model

Added founder-only backend endpoint:

- `GET /api/founder/insights`

Access is JWT-protected and requires `User.role` to be `founder` or `admin`. Regular users receive `403 FOUNDER_ACCESS_REQUIRED`.

Added hidden frontend page:

- `/founder-insights`

The page is not linked from the main product navigation and displays only aggregate metrics. It does not show user email, CV text, JD text or feedback comments.

## Founder Questions Now Answerable

- Where are beta users dropping off in the product funnel?
- Are users finding analysis, roadmap and interview feedback useful?
- Which missing skills appear most often?
- Is average matching score healthy or too low/high?
- Are users using the learning loop after roadmap generation?

## Files Changed

Backend:

- `backend/app/main.py`
- `backend/app/routers/founder_insights.py`
- `backend/app/schemas/founder_insights.py`
- `backend/tests/test_founder_insights.py`

Frontend:

- `frontend/lib/api/founder-insights.ts`
- `frontend/app/founder-insights/page.tsx`

Context/docs:

- `context/PHASE_7_7_FOUNDER_INSIGHTS_REPORT.md`
- `context/API_CONTRACTS.md`
- `context/CHANGELOG.md`
- `context/CURRENT_STATUS.md`
- `context/KNOWN_ISSUES.md`

## Limitations

- This is aggregate founder insight, not analytics infrastructure.
- Funnel counts are lifetime counts, not time-windowed cohorts.
- Common missing skills use stored missing skill lists, not advanced NLP.
- Confidence counts may change if matcher logic changes because analysis debug fields are still recomputed.
- Rerun-after-roadmap is inferred from records, not a dedicated event.
- There is no charting, export, segmentation or admin user management.

## Verification

- `python -m compileall app tests` passed.
- `pytest` passed: 59 tests.
- `pip check` passed.
- `npm run lint` passed.
- `npm run build` passed.

## Recommendation Before Next Phase

Use `/founder-insights` during beta review sessions to decide whether the next improvement should focus on matching calibration, roadmap usefulness, interview usefulness or onboarding funnel drop-off. Avoid adding heavier analytics until there is enough beta usage to justify it.
