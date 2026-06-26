from pathlib import Path

import pytest

from app.ml.training_infra import (
    parse_dataset_metadata,
    parse_experiment_metadata,
    parse_model_metadata,
    parse_training_config,
)


BACKEND_DIR = Path(__file__).resolve().parents[1]
ML_WORKSPACE = BACKEND_DIR / "ml"


def test_parse_dataset_metadata():
    metadata = parse_dataset_metadata(ML_WORKSPACE / "datasets" / "dataset_v2_metadata.json")

    assert metadata["dataset_id"] == "careeros_synthetic_matching"
    assert metadata["version"] == "dataset_v2"
    assert metadata["total_cases"] == 300


def test_parse_model_registry_metadata():
    metadata = parse_model_metadata(ML_WORKSPACE / "registry" / "hybrid_matching_model_v1.json")

    assert metadata["model_name"] == "hybrid_matching_model"
    assert metadata["model_version"] == "hybrid_matching_model_v1"
    assert metadata["production_safe"] is False


def test_parse_experiment_metadata():
    metadata = parse_experiment_metadata(ML_WORKSPACE / "experiments" / "experiment_template.json")

    assert metadata["experiment_id"] == "exp_template"
    assert metadata["status"] == "draft"
    assert isinstance(metadata["metrics"], dict)


def test_parse_training_config():
    config = parse_training_config(ML_WORKSPACE / "configs" / "training_config.json")

    assert config["random_seed"] == 42
    assert config["dataset_version"] == "dataset_v3"
    assert config["split_ratio"]["train"] == 0.75


def test_dataset_metadata_rejects_missing_fields(tmp_path):
    invalid = tmp_path / "invalid_dataset.json"
    invalid.write_text('{"dataset_id": "broken"}', encoding="utf-8")

    with pytest.raises(ValueError, match="thiếu field bắt buộc"):
        parse_dataset_metadata(invalid)