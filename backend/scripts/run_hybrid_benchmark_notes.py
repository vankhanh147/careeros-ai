"""Hybrid Matching V3 evaluation checklist for CareerOS Benchmark U01-U10.

This helper does not call the API or database. It runs the current deterministic
matcher against short canonical notes and prints production score plus hybrid
candidate metadata. Use raw anonymized benchmark artifacts when available.
"""

from __future__ import annotations

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.services.resume_job_matcher import analyze_resume_job_match  # noqa: E402

CASES = [
    ("U01", ".NET Backend Intern", ".NET Backend JD"),
    ("U02", "Node.js Backend", ".NET Backend JD"),
    ("U03", "React Frontend", "React Frontend JD"),
    ("U04", "React Frontend", ".NET Backend JD"),
    ("U05", "AI/Python Backend", ".NET Backend JD"),
    ("U06", ".NET Backend", "React Frontend JD"),
    ("U07", "Flutter Mobile", "AI/ML JD"),
    ("U08", "Data Analyst", ".NET Backend JD"),
    ("U09", "Cybersecurity", "React Frontend JD"),
    ("U10", "Marketing/Business", ".NET Backend JD"),
]


def main() -> None:
    print("CareerOS Hybrid Matching V3 evaluation checklist")
    print("=" * 52)
    print("Hybrid score is evaluation-only and must not replace production score.")
    print()
    for case_id, cv_persona, jd_target in CASES:
        resume_text = f"CV persona: {cv_persona}. Add full anonymized CV text here for real rerun."
        jd_text = f"JD target: {jd_target}. Add full anonymized JD text here for real rerun."
        result = analyze_resume_job_match(resume_text, jd_text)
        hybrid = result["hybrid_evaluation"]
        semantic = result["semantic_insights"]
        print(f"{case_id}: {cv_persona} -> {jd_target}")
        print(f"  final_score: {result['match_score']}")
        print(f"  hybrid_score_candidate: {hybrid['hybrid_score_candidate']}")
        print(f"  semantic_available: {semantic['enabled']}")
        print(f"  notes: {'; '.join(hybrid['explanation_notes'][:2])}")
        print("  manual review: ____")
        print()


if __name__ == "__main__":
    main()