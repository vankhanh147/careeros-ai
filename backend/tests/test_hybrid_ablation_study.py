from pathlib import Path

from scripts.run_hybrid_ablation_study import (
    ABLATION_CONFIGS,
    METADATA_PATH,
    STRUCTURED_CORE_KEYS,
    build_metrics,
    select_structured_features,
)
from scripts.train_matching_model_hybrid import HYBRID_MODEL_PATH


def test_ablation_configs_are_importable():
    keys = {config.key for config in ABLATION_CONFIGS}

    assert keys == {
        "text_only",
        "structured_without_rule_score",
        "structured_core_only",
        "full_hybrid",
    }


def test_feature_exclusion_removes_rule_based_score():
    row = {
        "structured_features": {
            "rule_based_score": 88,
            "skill_score": 40,
            "role_alignment_score": 20,
        }
    }

    selected = select_structured_features(row, ("skill_score", "role_alignment_score"))

    assert selected == {"skill_score": 40, "role_alignment_score": 20}
    assert "rule_based_score" not in selected


def test_structured_core_keys_are_minimal_and_stable():
    assert "rule_based_score" not in STRUCTURED_CORE_KEYS
    assert "role_alignment_score" in STRUCTURED_CORE_KEYS
    assert "evidence_score" in STRUCTURED_CORE_KEYS
    assert "missing_critical_skill_count" in STRUCTURED_CORE_KEYS


def test_metrics_output_has_required_keys():
    labels = ["good", "medium", "weak", "mismatch"]
    predictions = ["good", "medium", "medium", "mismatch"]
    rows = [
        {"source_category": "exact_fit"},
        {"source_category": "same_role_different_stack"},
        {"source_category": "weak_cv"},
        {"source_category": "non_it_mismatch"},
    ]

    metrics = build_metrics(labels, predictions, rows)

    assert {"accuracy", "macro_f1", "confusion_matrix", "category_errors"}.issubset(metrics)
    assert metrics["weak_errors"] == 1
    assert metrics["good_to_medium"] == 0
    assert metrics["mismatch_to_medium"] == 0


def test_ablation_metadata_path_does_not_overwrite_hybrid_artifact():
    assert Path(METADATA_PATH).name == "hybrid_ablation_metadata.json"
    assert Path(METADATA_PATH) != Path(HYBRID_MODEL_PATH)

