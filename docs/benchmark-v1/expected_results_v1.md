# Expected Results V1

V1 is the pre-Phase 6.5 matcher baseline. It relied heavily on rule-based skill overlap, keyword overlap, optional semantic similarity, length sanity and early skill-gap logic. It did not yet apply strong role-family detection, stack mismatch penalty, critical skill weighting, evidence-aware scoring or confidence gating.

## V1 Baseline Scores

| case_id | Scenario | V1 score | V1 interpretation |
| --- | --- | ---: | --- |
| U01 | .NET Backend Intern -> .NET Backend JD | 72.6 | Reasonable high fit, but evidence quality still needs inspection. |
| U02 | Node.js Backend -> .NET Backend JD | 75.5 | Too high for same-role different-stack; stack mismatch was under-penalized. |
| U03 | React Frontend -> React Frontend JD | 95.8 | Strong fit, but likely over-confident/perfect-looking. |
| U04 | React Frontend -> .NET Backend JD | 58.7 | Too high for frontend/backend mismatch. |
| U05 | AI/Python Backend -> .NET Backend JD | 72.6 | Too high if .NET/C#/ASP.NET evidence is weak; transferable skills inflated fit. |
| U06 | .NET Backend -> React Frontend JD | 58.7 | Too high for backend/frontend reverse mismatch. |
| U07 | Flutter Mobile -> AI/ML JD | 60.5 | Too high for mobile to AI cross-domain unless strong ML evidence exists. |
| U08 | Data Analyst -> .NET Backend JD | 42.5 | Closer to expected, but explanation should separate SQL/data overlap from backend readiness. |
| U09 | Cybersecurity -> React Frontend JD | 51.2 | Too high for security/frontend mismatch. |
| U10 | Marketing/Business -> .NET Backend JD | 44.2 | Too high for non-IT/business mismatch. |

## Main V1 Problems

- Generic technology terms such as Git, API, SQL and database could inflate score.
- Same role family but wrong stack could look too strong.
- Frontend/backend role mismatch was not penalized enough.
- Transferable skills were not separated from technical role fit.
- CV evidence depth was not measured strongly enough.
- Confidence was implicit, so short or shallow CVs could look overly certain.
