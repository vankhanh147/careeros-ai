# Expected Results V2.1

Date: 2026-06-15
Matcher version: Matching Scoring V2.1
Semantic mode for this rerun: disabled (`SENTENCE_TRANSFORMERS_ENABLED=false`), matching the Render Free production recommendation.

This file replaces the previous V2 TBD table with rerun scores from the current deterministic matcher. The repository does not contain the original raw 10 beta CV/JD files, so the rerun uses canonical benchmark texts derived from `benchmark_cases.md` and `context/BETA_REVIEW_V1.md`. Treat these scores as internal regression guardrails, not public ML labels.

## Target Ranges By Category

| Category | Acceptable V2 range | Notes |
| --- | ---: | --- |
| Exact fit | 75-90 | Strong role, stack, critical skills and evidence alignment. |
| Strong exact frontend fit | 80-90 | Keep high, but avoid near-perfect scores unless evidence is exceptional. |
| Same role different stack | 50-70 | Preserve transferable role credit while showing stack gap. |
| Role mismatch | 25-50 | Frontend/backend or backend/frontend mismatch should not pass as good fit. |
| Cross-domain transferable | 35-60 | Partial credit for real transferable skills, but clear gap remains. |
| Non-IT mismatch | 10-35 | Non-IT/business profiles should stay low for technical backend/frontend JDs. |

## Rerun Results

| case_id | Category | V1 score | final_score_v2.1 | Target range | Confidence | CV role -> JD role | CV stacks -> JD stacks | Calibration status |
| --- | --- | ---: | ---: | ---: | --- | --- | --- | --- |
| U01 | Exact backend fit | 72.6 | 81.9 | 75-90 | Medium | backend -> backend | devops_container, dotnet_backend -> devops_container, dotnet_backend | Pass |
| U02 | Same role different stack | 75.5 | 62.9 | 50-70 | Medium | backend -> backend | node_backend -> devops_container, dotnet_backend | Pass |
| U03 | Exact frontend fit | 95.8 | 85.7 | 80-90 | Medium | frontend -> frontend | react_frontend -> react_frontend | Pass |
| U04 | Frontend/backend mismatch | 58.7 | 40.1 | 25-50 | Medium | frontend -> backend | react_frontend -> devops_container, dotnet_backend | Pass |
| U05 | Transferable Python backend vs .NET | 72.6 | 59.4 | 35-60 | Medium | backend -> backend | python_backend -> devops_container, dotnet_backend | Pass |
| U06 | Backend/frontend mismatch | 58.7 | 36.9 | 25-50 | Medium | backend -> frontend | devops_container, dotnet_backend -> react_frontend | Pass |
| U07 | Mobile to AI cross-domain | 60.5 | 39.3 | 35-60 | Medium | mobile -> ai/data | mobile_flutter, python_backend -> python_backend | Pass |
| U08 | Data/SQL overlap vs backend | 42.5 | 38.6 | 35-60 | Medium | ai/data -> backend | python_backend -> devops_container, dotnet_backend | Pass |
| U09 | Security/frontend mismatch | 51.2 | 44.5 | 25-50 | Medium | frontend -> frontend | none -> react_frontend | Pass |
| U10 | Non-IT/business vs backend | 44.2 | 11.7 | 10-35 | Low | general software -> backend | none -> devops_container, dotnet_backend | Pass |

## Per-Case Details

### U01: .NET Backend Intern -> .NET Backend JD

- final_score_v2.1: 81.9
- confidence: Medium
- detected_role_family: backend -> backend
- detected_stack_group: devops_container, dotnet_backend -> devops_container, dotnet_backend
- role_alignment_score: 20.0
- evidence_score: 15.7
- critical_skills: authentication, backend, c#, docker, jwt, postgresql, sql
- major_missing_skills: orm, postgresql, testing, unit testing
- evaluation note: Exact backend fit stays high without looking perfect. Missing ORM/testing still creates useful improvement direction.

### U02: Node.js Backend -> .NET Backend JD

- final_score_v2.1: 62.9
- confidence: Medium
- detected_role_family: backend -> backend
- detected_stack_group: node_backend -> devops_container, dotnet_backend
- role_alignment_score: 16.0
- evidence_score: 15.3
- critical_skills: authentication, backend, c#, docker, jwt, postgresql, sql
- major_missing_skills: .net, asp.net core, c#, docker, orm, postgresql, testing, unit testing
- evaluation note: Same role family gets partial credit, but .NET stack gap is now visible and no longer over-scored like V1.

### U03: React Frontend -> React Frontend JD

- final_score_v2.1: 85.7
- confidence: Medium
- detected_role_family: frontend -> frontend
- detected_stack_group: react_frontend -> react_frontend
- role_alignment_score: 20.0
- evidence_score: 14.2
- critical_skills: authentication, frontend, javascript, next.js, react, typescript
- major_missing_skills: none detected
- evaluation note: Strong frontend exact fit remains high but drops from V1's near-perfect 95.8.

### U04: React Frontend -> .NET Backend JD

- final_score_v2.1: 40.1
- confidence: Medium
- detected_role_family: frontend -> backend
- detected_stack_group: react_frontend -> devops_container, dotnet_backend
- role_alignment_score: 0.0
- evidence_score: 14.0
- critical_skills: authentication, backend, c#, docker, jwt, postgresql, sql
- major_missing_skills: .net, asp.net core, c#, docker, postgresql, sql, testing, unit testing
- evaluation note: Role mismatch is now penalized enough to land in the expected mismatch range.

### U05: AI/Python Backend -> .NET Backend JD

- final_score_v2.1: 59.4
- confidence: Medium
- detected_role_family: backend -> backend
- detected_stack_group: python_backend -> devops_container, dotnet_backend
- role_alignment_score: 16.0
- evidence_score: 15.0
- critical_skills: authentication, backend, c#, docker, jwt, postgresql, sql
- major_missing_skills: .net, asp.net core, c#, docker, sql, testing, unit testing
- evaluation note: Backend/API/database transfer is preserved, but missing .NET stack keeps score below exact-fit.

### U06: .NET Backend -> React Frontend JD

- final_score_v2.1: 36.9
- confidence: Medium
- detected_role_family: backend -> frontend
- detected_stack_group: devops_container, dotnet_backend -> react_frontend
- role_alignment_score: 0.0
- evidence_score: 14.0
- critical_skills: authentication, frontend, javascript, next.js, react, typescript
- major_missing_skills: authentication, javascript, next.js, react, typescript
- evaluation note: Reverse backend/frontend mismatch now lands safely in the role-mismatch range.

### U07: Flutter Mobile -> AI/ML JD

- final_score_v2.1: 39.3
- confidence: Medium
- detected_role_family: mobile -> ai/data
- detected_stack_group: mobile_flutter, python_backend -> python_backend
- role_alignment_score: 8.0
- evidence_score: 14.7
- critical_skills: ai, machine learning, nlp, numpy, pandas, python, pytorch, scikit-learn, sentence transformers, tensorflow
- major_missing_skills: ai, machine learning, nlp, numpy, pandas, pytorch, scikit-learn, sentence transformers
- evaluation note: Mobile profile gets limited transfer credit for Python/API but clear AI/ML gap remains.

### U08: Data Analyst -> .NET Backend JD

- final_score_v2.1: 38.6
- confidence: Medium
- detected_role_family: ai/data -> backend
- detected_stack_group: python_backend -> devops_container, dotnet_backend
- role_alignment_score: 4.0
- evidence_score: 14.8
- critical_skills: authentication, backend, c#, docker, jwt, postgresql, sql
- major_missing_skills: .net, asp.net core, authentication, backend, c#, docker, jwt, rest api, testing, unit testing
- evaluation note: SQL/data overlap is recognized, but backend engineering readiness is not overestimated.

### U09: Cybersecurity -> React Frontend JD

- final_score_v2.1: 44.5
- confidence: Medium
- detected_role_family: frontend -> frontend
- detected_stack_group: none -> react_frontend
- role_alignment_score: 13.3
- evidence_score: 14.7
- critical_skills: authentication, frontend, javascript, next.js, react, typescript
- major_missing_skills: api, css, html, javascript, next.js, react, rest api, typescript
- evaluation note: Score drops into role-mismatch range. Remaining weakness: security profiles with basic JavaScript can still look partially frontend-adjacent.

### U10: Marketing/Business -> .NET Backend JD

- final_score_v2.1: 11.7
- confidence: Low
- detected_role_family: general software -> backend
- detected_stack_group: none -> devops_container, dotnet_backend
- role_alignment_score: 6.7
- evidence_score: 0.0
- critical_skills: authentication, backend, c#, docker, jwt, postgresql, sql
- major_missing_skills: .net, api, asp.net core, authentication, backend, c#, database, docker, git, github, jwt, orm, postgresql, rest api, sql, testing, unit testing
- evaluation note: Non-IT mismatch is now correctly low and low-confidence.

## Calibration Notes

Small V2.1 calibration was applied after the initial rerun showed over-scoring from negated phrases such as `no C#`, `no .NET`, `no React` and `no backend`. The matcher now ignores negated skill mentions during skill detection and evidence scoring. Role-family detection also gives mobile and ai/data profiles priority when backend evidence is only generic API/auth/data overlap without a real backend stack signal.

## Improvement Criteria Check

- Exact fit stays high: U01 and U03 pass.
- Same-role different-stack remains useful but not inflated: U02 and U05 pass.
- Role mismatch decreases from V1: U04, U06 and U09 pass.
- Cross-domain transfer remains modest: U07 and U08 pass.
- Non-IT mismatch is clearly lower than V1: U10 pass.

Current confidence in matcher V2.1: good enough for controlled beta, with manual review recommended for unusual CV wording and mixed-role profiles.
