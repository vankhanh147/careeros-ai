# Benchmark Cases V1

These 10 cases are the official internal benchmark set for CareerOS AI Resume <-> JD Matching. V1 scores are from the beta review notes supplied for Phase 6.6. V2 scores are only filled when an exact rerun value is known; otherwise they remain TBD.

| case_id | CV persona | JD target | Expected behavior | V1 score | V2 score | Known issue / note | Evaluation purpose |
| --- | --- | --- | --- | ---: | --- | --- | --- |
| U01 | .NET Backend Intern | .NET Backend JD | Exact backend fit should score high, with strong role and stack alignment. | 72.6 | TBD | V1 was reasonable but should verify evidence and confidence in V2. | Exact backend fit |
| U02 | Node.js Backend | .NET Backend JD | Same role family but different backend stack should be medium, not exact-fit high. | 75.5 | TBD | V1 likely over-scored because backend/generic API overlap outweighed stack mismatch. | Same role family, different stack |
| U03 | React Frontend | React Frontend JD | Strong exact frontend fit should stay high but not unrealistically perfect. | 95.8 | TBD - reported reduced after Phase 6.5; exact score needs rerun | V1 over-scored near-perfect; V2 should preserve high fit while applying evidence/confidence discipline. | Exact frontend fit |
| U04 | React Frontend | .NET Backend JD | Frontend/backend mismatch should score low to medium-low. | 58.7 | TBD | V1 over-scored from generic software/API/Git overlap. | Frontend/backend role mismatch |
| U05 | AI/Python Backend | .NET Backend JD | Transferable backend/Python/AI skills should get partial credit but stack mismatch must be visible. | 72.6 | TBD | V1 likely too high for .NET target if C#/ASP.NET evidence is missing. | Transferable backend/AI skills vs .NET stack |
| U06 | .NET Backend | React Frontend JD | Backend/frontend reverse mismatch should score low to medium-low. | 58.7 | TBD - reported reduced after Phase 6.5; exact score needs rerun | V1 over-scored from generic web/API overlap. | Backend/frontend reverse mismatch |
| U07 | Flutter Mobile | AI/ML JD | Cross-domain mobile to AI should score low to medium unless Python/ML evidence is strong. | 60.5 | TBD | V1 likely over-scored transferable/general tech overlap. | Mobile to AI cross-domain |
| U08 | Data Analyst | .NET Backend JD | Data/SQL overlap should count, but backend engineering gap should keep score modest. | 42.5 | TBD | V1 was closer to expected but needs role-family and evidence explanation. | Data/SQL overlap vs backend role |
| U09 | Cybersecurity | React Frontend JD | Security/frontend mismatch should score low to medium-low despite generic web/security overlap. | 51.2 | TBD - reported reduced after Phase 6.5; exact score needs rerun | V1 likely inflated by broad tech keywords. | Security/frontend mismatch |
| U10 | Marketing/Business | .NET Backend JD | Non-IT/business profile should score low unless there is real software evidence. | 44.2 | TBD - possible 52.5 from manual rerun, needs verify | If V2 is 52.5, that is likely still too high for non-IT mismatch and should be investigated. | Non-IT/business profile vs backend JD |

## Case Notes

- U01 and U03 are anchor exact-fit cases. They should remain high after improvements.
- U02 and U05 test whether same-family or transferable skills are handled without pretending the stack is exact.
- U04, U06 and U09 test role mismatch penalties.
- U07 and U08 test cross-domain transferable overlap.
- U10 is the key non-IT mismatch guardrail.
