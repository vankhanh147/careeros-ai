"""Semantic benchmark helper for CareerOS Phase 8.3.

This script does not call the API or database. It uses short canonical notes for
U01-U10 and only computes semantic similarity when SENTENCE_TRANSFORMERS_ENABLED
is explicitly true and the model can be loaded locally.
"""

from __future__ import annotations

import os
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.ai.semantic_matcher import build_semantic_insights  # noqa: E402

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
    print("CareerOS Semantic Benchmark V1 helper")
    print("=" * 42)
    print(f"SENTENCE_TRANSFORMERS_ENABLED={os.getenv('SENTENCE_TRANSFORMERS_ENABLED', 'false')}")
    print(f"SENTENCE_TRANSFORMERS_MODEL_NAME={os.getenv('SENTENCE_TRANSFORMERS_MODEL_NAME', 'all-MiniLM-L6-v2')}")
    print("This helper uses short canonical text only. Use raw anonymized CV/JD artifacts when available.")
    print()

    for case_id, cv_persona, jd_target in CASES:
        resume_text = f"CV persona: {cv_persona}. Project and skill evidence should be filled from the benchmark artifact."
        jd_text = f"JD target: {jd_target}. Requirements should be filled from the benchmark artifact."
        insight = build_semantic_insights(resume_text, jd_text)
        similarity = insight["resume_jd_similarity"]
        similarity_text = f"{similarity:.4f}" if similarity is not None else "skipped"
        print(f"{case_id}: {cv_persona} -> {jd_target}")
        print(f"  enabled: {insight['enabled']}")
        print(f"  similarity: {similarity_text}")
        print(f"  reason: {insight['reason'] or 'ok'}")
        print("  manual note: ____")
        print()


if __name__ == "__main__":
    main()