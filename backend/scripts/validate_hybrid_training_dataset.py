"""Validate Phase 9.2 hybrid training dataset."""

from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.ml.features import HYBRID_STRUCTURED_FEATURE_KEYS


DATASET_PATH = ROOT_DIR / "docs" / "datasets" / "synthetic" / "hybrid_training_dataset.json"
EXPECTED_ROW_COUNT = 300
VALID_LABELS = {"good", "medium", "weak", "mismatch"}
REQUIRED_ROW_FIELDS = {"case_id", "text_input", "structured_features", "label", "source_category", "expected_score_range"}
SCORE_FEATURES = {
    "rule_based_score",
    "skill_score",
    "keyword_score",
    "role_alignment_score",
    "evidence_score",
    "length_sanity",
    "semantic_similarity",
    "hybrid_score_candidate",
    "taxonomy_component",
}
COUNT_FEATURES = {
    "critical_skill_count",
    "missing_critical_skill_count",
    "matched_skill_count",
    "missing_skill_count",
    "stack_group_match_count",
    "normalized_skill_overlap_count",
    "related_skill_support_count",
}
BOOLEAN_NUMERIC_FEATURES = {"role_family_match", "semantic_available"}
MOJIBAKE_PATTERN = re.compile(r"\ufffd|M\?|Kh\?|H\?\?|tr\?|\?\?\?")
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_PATTERN = re.compile(r"(?<!\d)(?:\+?\d[\s.-]?){9,14}(?!\d)")


def load_dataset(path: Path = DATASET_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_hybrid_dataset(payload: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    rows = payload.get("rows")
    if not isinstance(rows, list):
        return {"errors": ["Field rows phải là list."], "warnings": [], "summary": {}}
    if payload.get("dataset_type") != "hybrid_training":
        errors.append("dataset_type phải là hybrid_training.")
    if payload.get("row_count") != EXPECTED_ROW_COUNT:
        errors.append(f"row_count phải là {EXPECTED_ROW_COUNT}.")
    if len(rows) != EXPECTED_ROW_COUNT:
        errors.append(f"Số row phải là {EXPECTED_ROW_COUNT}, hiện có {len(rows)}.")

    case_ids: set[str] = set()
    label_counts: dict[str, int] = {}
    category_counts: dict[str, int] = {}

    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            errors.append(f"Row #{index} không phải object.")
            continue
        case_id = str(row.get("case_id") or f"row #{index}")
        if case_id in case_ids:
            errors.append(f"case_id bị trùng: {case_id}.")
        case_ids.add(case_id)

        missing_fields = sorted(REQUIRED_ROW_FIELDS - set(row))
        if missing_fields:
            errors.append(f"{case_id} thiếu field: {', '.join(missing_fields)}.")

        label = str(row.get("label") or "")
        label_counts[label] = label_counts.get(label, 0) + 1
        if label not in VALID_LABELS:
            errors.append(f"{case_id} có label không hợp lệ: {label}.")

        category = str(row.get("source_category") or "")
        category_counts[category] = category_counts.get(category, 0) + 1

        text_input = str(row.get("text_input") or "")
        if not text_input.strip():
            errors.append(f"{case_id} thiếu text_input.")

        structured = row.get("structured_features")
        if not isinstance(structured, dict):
            errors.append(f"{case_id} structured_features phải là object.")
            continue
        missing_keys = sorted(set(HYBRID_STRUCTURED_FEATURE_KEYS) - set(structured))
        if missing_keys:
            errors.append(f"{case_id} thiếu structured feature: {', '.join(missing_keys)}.")
        _validate_structured_features(case_id, structured, errors, warnings)

        blob = json.dumps(row, ensure_ascii=False)
        if MOJIBAKE_PATTERN.search(blob):
            errors.append(f"{case_id} có dấu hiệu mojibake.")
        if EMAIL_PATTERN.search(blob):
            errors.append(f"{case_id} có dấu hiệu email/PII.")
        if PHONE_PATTERN.search(blob):
            errors.append(f"{case_id} có dấu hiệu số điện thoại/PII.")

    return {
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "row_count": len(rows),
            "label_counts": dict(sorted(label_counts.items())),
            "category_counts": dict(sorted(category_counts.items())),
        },
    }


def _validate_structured_features(case_id: str, structured: dict[str, Any], errors: list[str], warnings: list[str]) -> None:
    for key, value in structured.items():
        if isinstance(value, float) and math.isnan(value):
            errors.append(f"{case_id}.{key} là NaN.")
        if key in SCORE_FEATURES and isinstance(value, (int, float)) and not (0 <= float(value) <= 100):
            errors.append(f"{case_id}.{key} nằm ngoài range 0-100: {value}.")
        if key == "confidence" and isinstance(value, (int, float)) and not (0 <= float(value) <= 1):
            errors.append(f"{case_id}.confidence nằm ngoài range 0-1: {value}.")
        if key == "confidence_adjustment" and isinstance(value, (int, float)) and not (-20 <= float(value) <= 20):
            errors.append(f"{case_id}.confidence_adjustment nằm ngoài range -20 đến 20: {value}.")
        if key in COUNT_FEATURES and isinstance(value, (int, float)) and float(value) < 0:
            errors.append(f"{case_id}.{key} không được âm: {value}.")
        if key in BOOLEAN_NUMERIC_FEATURES and value not in {0, 1, 0.0, 1.0}:
            errors.append(f"{case_id}.{key} phải là 0/1: {value}.")
    if structured.get("rule_based_score", 0) == 0:
        warnings.append(f"{case_id} có rule_based_score = 0, nên review nếu không phải mismatch rất mạnh.")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    payload = load_dataset()
    result = validate_hybrid_dataset(payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

