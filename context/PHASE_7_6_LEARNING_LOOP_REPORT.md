# Phase 7.6 - User Learning Loop & Progress Tracking Lite

Date: 2026-06-16

## Goal

Phase 7.6 turns CareerOS AI from one-shot outputs into a lightweight learning loop. The scope stays MVP-friendly: no productivity/task manager, no gamification, no new analytics system and no infrastructure change.

## Logic Added

### Roadmap Item Completion Lite

- Each roadmap item can now be marked `completed=true` or `completed=false` inside the existing `LearningRoadmap.items` JSON payload.
- No database schema change was introduced.
- Old roadmap items without `completed` are treated as not completed by backend/frontend defaults.
- Only the latest roadmap can be updated through the API and UI.
- The roadmap page shows a lightweight summary such as `Đã hoàn thành 2/6 mục roadmap`.

### Dashboard Learning Loop Reminders

Dashboard summary now returns additive learning-loop signals:

- `latest_roadmap.completed_items`
- `latest_roadmap.total_items`
- `has_new_resume_after_analysis`
- `should_rerun_analysis`
- `learning_loop_summary`

Dashboard uses these signals to recommend:

- Run Resume ↔ JD Matching again when a newer CV was uploaded after the latest analysis.
- Practice Mock Interview when the user has analysis and roadmap but has not practiced yet.
- Update CV and rerun matching when some roadmap items are completed.

### Smart Rerun Signal

`should_rerun_analysis=true` when:

- the latest resume is newer than the latest analysis, or
- the latest roadmap has at least one completed item.

The app does not rerun analysis automatically. It only suggests the next action.

## Files Changed

Backend:

- `backend/app/schemas/roadmap.py`
- `backend/app/routers/roadmaps.py`
- `backend/app/schemas/dashboard.py`
- `backend/app/routers/dashboard.py`
- `backend/tests/test_roadmaps.py`
- `backend/tests/test_dashboard.py`

Frontend:

- `frontend/lib/api/roadmaps.ts`
- `frontend/lib/api/dashboard.ts`
- `frontend/app/roadmap/page.tsx`
- `frontend/app/dashboard/page.tsx`

Context/docs:

- `context/PHASE_7_6_LEARNING_LOOP_REPORT.md`
- `context/CURRENT_STATUS.md`
- `context/CHANGELOG.md`
- `context/API_CONTRACTS.md`
- `context/KNOWN_ISSUES.md`

## Schema Impact

No database schema change.

Completion state is stored in existing roadmap item JSON. This keeps the MVP simple and avoids a progress table.

## Tests Verified

- Roadmap item completion endpoint updates the latest roadmap item.
- Missing roadmap item index returns 404.
- Dashboard summary includes roadmap completion counts.
- Dashboard sets rerun signal when roadmap completion exists.
- Dashboard sets rerun signal when a newer CV exists after latest analysis.

Verification commands:

- `python -m compileall app tests` passed.
- `pytest` passed: 56 tests.
- `pip check` passed.
- `npm run lint` passed.
- `npm run build` passed.

## Known Limitations

- Completion is tracked only at roadmap-item level, not per action or per practice task.
- Only the latest roadmap can be updated by design.
- There is no progress chart, streak, badge or notification system.
- Completion is user-declared; CareerOS AI does not verify whether the practice task was actually completed.
- Since completion lives in JSON, future complex progress features may need a dedicated table, but that is intentionally postponed.

## Recommendation Before Next Phase

Use this Lite learning loop with real beta users before adding any richer progress feature. The next valuable step is to observe whether users actually mark roadmap items complete and rerun matching after updating CV.
