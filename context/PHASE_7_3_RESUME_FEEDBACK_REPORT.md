# Phase 7.3 - Resume Feedback & Rewrite Suggestions MVP

Date: 2026-06-15
Scope: add template-based resume feedback after Resume ? JD Analysis. No LLM API, no fine-tuning, no database schema change and no breaking API contract.

## 1. Logic Added

Phase 7.3 adds `resume_feedback` to the analysis response. This is an additive response field and is recomputed from current CV/JD text, similar to the existing debug preview and skill gap outputs.

The feedback engine is deterministic and uses existing matcher signals:

- `critical_skills`
- `missing_skills`
- role family detection
- stack group detection
- evidence score
- confidence
- matched skill evidence level

Output groups:

1. `critical_gaps`
2. `cv_wording_improvements`
3. `suggested_bullet_rewrites`
4. `missing_evidence_areas`
5. `recommended_next_edits`

Each item includes:

- `title`
- `message`
- `why_this_matters`
- `suggested_edit` when useful

## 2. Safety Rules

The engine intentionally avoids hallucination:

- It does not claim the user has a skill when the CV does not show evidence.
- It only gives concrete rewrite templates from evidenced skills.
- If a skill is missing, wording uses conditional language such as `If you actually used X...`.
- It does not rewrite the entire CV.
- It does not invent metrics, impact numbers or responsibilities.

## 3. Examples

### Missing critical skill

If JD requires JWT but CV does not show it:

- Message: `JD requires jwt, but the CV does not show clear evidence for it yet.`
- Suggested edit: `If you actually used jwt, add it to a project or experience bullet with your specific responsibility.`

### Weak project evidence

If the CV has matched skills but only shallow wording:

- Message: `The CV mentions api, backend, git, but the wording does not strongly prove what you built or owned.`
- Suggested edit: `Rewrite generic bullets with this pattern: Developed [feature] using [tech stack], responsible for [technical task], resulting in [real outcome if you can prove it].`

### Safe bullet rewrite

If CV has evidence for API/authentication/JWT:

- Suggested edit: `Developed backend REST API workflows with authentication/JWT support and clear request validation.`

If CV does not have the skill, the engine does not output this as a claim.

## 4. Frontend UX

`/analysis` now shows a concise section:

- Resume Improvement Suggestions
- Critical gaps
- CV wording improvements
- Suggested bullet rewrites
- Missing evidence areas
- Recommended next edits

The section appears only for detailed/current analysis cards, not compact history cards, to avoid turning history into a wall of text.

## 5. Benchmark Observations

Sanity checks were added for U01, U02, U04 and U10:

- U01 exact fit: does not spam critical gaps and still provides safe bullet rewrite templates.
- U02 same-role different-stack: gives stack transition advice and conditional `.NET/C#` guidance.
- U04 frontend ? backend mismatch: highlights role alignment issue instead of pretending frontend work is backend evidence.
- U10 non-IT ? backend mismatch: does not generate concrete backend rewrite claims and keeps conditional language.

## 6. Known Limitations

- The feedback engine is still heuristic and template-based.
- It depends on PDF text extraction quality.
- It cannot know whether a user truly implemented a skill unless the CV text shows evidence.
- It does not identify exact original CV bullet lines yet.
- It does not generate a full rewritten CV.
- It does not use LLMs or semantic rewriting, by design.

## 7. Future Improvements

Recommended future phases:

1. Add line-level/bullet-level extraction so suggestions can point to specific CV sections.
2. Add user confirmation flow: `I actually used this skill` before stronger rewrite suggestions.
3. Add exportable checklist for CV edits.
4. Collect beta feedback on whether suggestions are too generic or too strict.
5. Keep this system separate from any future LLM rewrite feature unless explicitly requested.
