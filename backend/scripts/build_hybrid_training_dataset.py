"""Build the Phase 9.2 hybrid training dataset.

Input: docs/datasets/synthetic/synthetic_cases.json
Output:
- docs/datasets/synthetic/hybrid_training_dataset.json
- docs/datasets/synthetic/hybrid_feature_schema.json

This is offline data preparation only. It does not change production scoring.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.ml.features import HYBRID_STRUCTURED_FEATURE_KEYS, build_hybrid_training_row
from app.services.resume_job_matcher import analyze_resume_job_match


INPUT_PATH = ROOT_DIR / "docs" / "datasets" / "synthetic" / "synthetic_cases.json"
OUTPUT_PATH = ROOT_DIR / "docs" / "datasets" / "synthetic" / "hybrid_training_dataset.json"
SCHEMA_PATH = ROOT_DIR / "docs" / "datasets" / "synthetic" / "hybrid_feature_schema.json"


def load_synthetic_cases(path: Path = INPUT_PATH) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    cases = payload.get("cases", payload if isinstance(payload, list) else [])
    if not isinstance(cases, list):
        raise ValueError("Synthetic dataset field 'cases' phải là list.")
    return [dict(case) for case in cases]


def build_hybrid_rows(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for case in cases:
        analysis = analyze_resume_job_match(
            str(case.get("resume_summary") or ""),
            str(case.get("job_description_summary") or ""),
        )
        rows.append(build_hybrid_training_row(case, analysis))
    return rows


def build_feature_schema() -> dict[str, Any]:
    numeric_features = [
        "rule_based_score",
        "skill_score",
        "keyword_score",
        "role_alignment_score",
        "evidence_score",
        "confidence",
        "length_sanity",
        "critical_skill_count",
        "missing_critical_skill_count",
        "matched_skill_count",
        "missing_skill_count",
        "role_family_match",
        "stack_group_match_count",
        "normalized_skill_overlap_count",
        "related_skill_support_count",
        "semantic_available",
        "semantic_similarity",
        "hybrid_score_candidate",
        "taxonomy_component",
        "confidence_adjustment",
    ]
    categorical_features = [
        "seniority_level",
        "category",
        "target_role",
        "candidate_stack",
        "jd_stack",
    ]
    return {
        "schema_version": "careeros-hybrid-training-dataset-v1",
        "language": "vi",
        "feature_source": "synthetic dataset + rule-based matcher metadata",
        "structured_feature_keys": list(HYBRID_STRUCTURED_FEATURE_KEYS),
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
        "required_row_fields": [
            "case_id",
            "text_input",
            "structured_features",
            "label",
            "source_category",
            "expected_score_range",
        ],
        "notes": [
            "Dataset này dùng cho evaluation/training offline, không thay production scoring.",
            "semantic_similarity sẽ bằng 0 khi semantic model disabled hoặc không khả dụng.",
        ],
    }


def write_outputs(rows: list[dict[str, Any]]) -> None:
    payload = {
        "schema_version": "careeros-hybrid-training-dataset-v1",
        "dataset_type": "hybrid_training",
        "source_dataset": "docs/datasets/synthetic/synthetic_cases.json",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "row_count": len(rows),
        "rows": rows,
    }
    OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    SCHEMA_PATH.write_text(json.dumps(build_feature_schema(), ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    cases = load_synthetic_cases()
    rows = build_hybrid_rows(cases)
    write_outputs(rows)
    print(f"Hybrid training rows: {len(rows)}")
    print(f"Dataset: {OUTPUT_PATH}")
    print(f"Schema: {SCHEMA_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

