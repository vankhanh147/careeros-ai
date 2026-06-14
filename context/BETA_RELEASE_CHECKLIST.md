# BETA_RELEASE_CHECKLIST.md

Date: 2026-06-15
Phase: 6.7 - Final Beta Stabilization

This checklist is the final manual gate before inviting real beta users to CareerOS AI.

## 1. Environment Readiness

- [ ] Backend production URL is reachable: `https://careeros-ai-backend.onrender.com/health`.
- [ ] Frontend production URL is reachable: `https://careeros-ai-bay.vercel.app`.
- [ ] Vercel `NEXT_PUBLIC_API_URL` points to the Render backend URL.
- [ ] Render `BACKEND_CORS_ORIGINS` includes the Vercel production domain.
- [ ] Render uses `PYTHON_VERSION=3.11.9` or `backend/runtime.txt`.
- [ ] Render uses `PORT=10000` and start command `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
- [ ] `SENTENCE_TRANSFORMERS_ENABLED=false` on Render Free unless the instance has enough resources.
- [ ] Supabase Storage env vars are set when testing production uploads.

## 2. Auth Flow

- [ ] Register with a new email succeeds.
- [ ] Duplicate email shows a friendly error.
- [ ] Login succeeds with the registered account.
- [ ] Wrong password shows a friendly error.
- [ ] Protected pages redirect unauthenticated users to `/login`.
- [ ] Logout returns user to `/login`.

## 3. Career Profile Flow

- [ ] `/profile` loads without crash for a new user.
- [ ] Empty state explains what to enter first.
- [ ] Save button is disabled when every field is empty.
- [ ] User can save target role, current level, skills, experience, projects, career goal and timeline.
- [ ] Returning to `/profile` shows saved data.

## 4. Documents Flow

- [ ] `/documents` loads without horizontal scroll on desktop and mobile.
- [ ] Upload CV PDF under 5MB succeeds.
- [ ] Wrong CV file type shows a friendly error.
- [ ] Upload JD PDF/TXT under 5MB succeeds.
- [ ] Paste JD with title/content succeeds.
- [ ] Edit JD pre-fills the form and saves correctly.
- [ ] Delete JD requires confirmation and refreshes the list.
- [ ] Delete CV requires confirmation and refreshes the list.
- [ ] Long filename, storage path and source URL wrap/truncate inside cards.
- [ ] Supabase Storage object appears after upload and is removed after delete when configured.

## 5. Analysis Flow

- [ ] `/analysis` shows a clear empty state when CV or JD is missing.
- [ ] User can select one CV and one JD.
- [ ] Resume <-> JD Matching completes without crash.
- [ ] Result shows match score, matched skills, missing skills, skill gap summary and improvement plan.
- [ ] Debug preview shows CV text preview and JD text preview.
- [ ] V2 breakdown shows role alignment, evidence score, confidence and final score.
- [ ] Feedback block submits useful/not useful once and shows a thank-you state.
- [ ] History shows the latest analysis.

## 6. Roadmap Flow

- [ ] `/roadmap` loads with or without existing analysis.
- [ ] Generate roadmap from profile only when no analysis is selected.
- [ ] Generate roadmap from selected analysis.
- [ ] Timeline parser handles `1 tu?n`, `2 tu?n`, `1 th?ng` and empty timeline.
- [ ] Roadmap items show focus, skills, actions and expected output.
- [ ] Feedback block submits once and shows a thank-you state.
- [ ] History can select a previous roadmap.

## 7. Mock Interview Flow

- [ ] `/interview` loads with or without existing analysis.
- [ ] Start interview with target role or selected analysis.
- [ ] Session creates about 5 questions.
- [ ] Submit answer returns score and feedback.
- [ ] Empty answer cannot be submitted.
- [ ] Finish is available after answers are completed.
- [ ] Finished session shows average score and summary.
- [ ] Feedback block submits once and shows a thank-you state.
- [ ] History can select previous sessions.

## 8. Dashboard Flow

- [ ] `/dashboard` loads summary safely for a new user.
- [ ] Dashboard shows profile/CV/JD counts correctly.
- [ ] Progress indicator reflects current MVP flow state.
- [ ] Primary next action changes dynamically by user state.
- [ ] Latest analysis, roadmap and interview cards show safe empty states.
- [ ] Interview in progress shows `?ang luy?n` and `?i?m: Ch?a ho?n th?nh`.
- [ ] Refresh CTA reloads dashboard without full page reload.

## 9. Error, Loading and Empty States

- [ ] Backend offline shows a friendly connection error.
- [ ] 401/expired token suggests logging in again.
- [ ] 404 selected data missing suggests reload or reselect.
- [ ] File validation errors are understandable.
- [ ] Loading labels are short and in Vietnamese.
- [ ] Empty states include a next action CTA where relevant.

## 10. Internal Quality Checks

- [ ] Backend `python -m compileall app tests` passes.
- [ ] Backend `pytest` passes.
- [ ] Backend `pip check` passes.
- [ ] Frontend `npm run lint` passes.
- [ ] Frontend `npm run build` passes.
- [ ] No `.env` or uploaded files are committed.
- [ ] No service role key is exposed to frontend.
- [ ] `docs/benchmark-v1/` is used before changing matcher logic.

## Release Decision

Release beta only when:

- Core user flow works end-to-end: register -> profile -> CV/JD -> analysis -> roadmap -> interview -> dashboard.
- No crash is observed in the main flow.
- Known limitations are acceptable and documented.
- At least one production smoke test has been completed on Render + Vercel.
