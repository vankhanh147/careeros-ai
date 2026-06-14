"""Manual benchmark checklist for CareerOS Benchmark V1.

This script does not call the API or database. It prints the official
U01-U10 benchmark cases so a developer can rerun them manually before
changing the Resume <-> JD matcher.
"""

CASES = [
    ("U01", ".NET Backend Intern", ".NET Backend JD", "72.6", "75-90", "exact backend fit"),
    ("U02", "Node.js Backend", ".NET Backend JD", "75.5", "50-70", "same role, different stack"),
    ("U03", "React Frontend", "React Frontend JD", "95.8", "80-90", "exact frontend fit"),
    ("U04", "React Frontend", ".NET Backend JD", "58.7", "25-50", "frontend/backend mismatch"),
    ("U05", "AI/Python Backend", ".NET Backend JD", "72.6", "35-60", "transferable backend/AI vs .NET"),
    ("U06", ".NET Backend", "React Frontend JD", "58.7", "25-50", "backend/frontend mismatch"),
    ("U07", "Flutter Mobile", "AI/ML JD", "60.5", "35-60", "mobile to AI cross-domain"),
    ("U08", "Data Analyst", ".NET Backend JD", "42.5", "35-60", "data/SQL overlap vs backend"),
    ("U09", "Cybersecurity", "React Frontend JD", "51.2", "25-50", "security/frontend mismatch"),
    ("U10", "Marketing/Business", ".NET Backend JD", "44.2", "10-35", "non-IT/business mismatch"),
]


def main() -> None:
    print("CareerOS Benchmark V1 manual rerun checklist")
    print("=" * 52)
    print("Record current score, confidence, role families, stack groups, critical skills, and notes.")
    print()
    for case_id, cv, jd, v1, target, purpose in CASES:
        print(f"{case_id}: {cv} -> {jd}")
        print(f"  purpose: {purpose}")
        print(f"  V1 score: {v1}")
        print(f"  V2 target range: {target}")
        print("  current rerun score: ____")
        print("  confidence: ____")
        print("  notes: ____")
        print()
    print("Update docs/benchmark-v1/expected_results_v2.md when exact rerun scores are confirmed.")


if __name__ == "__main__":
    main()
