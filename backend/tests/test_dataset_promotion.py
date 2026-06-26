import json
import subprocess
import sys
from pathlib import Path

import pytest

from app.ml.training_infra import parse_promotion_config, validate_dataset_promotion


BACKEND_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = BACKEND_DIR.parent
DATASETS_DIR = BACKEND_DIR / "ml" / "datasets"
DEFAULT_CONFIG_PATH = BACKEND_DIR / "ml" / "configs" / "dataset_promotion_config.json"


def write_config(tmp_path: Path, **overrides):
    config = parse_promotion_config(DEFAULT_CONFIG_PATH)
    config.update(overrides)
    path = tmp_path / "promotion_config.json"
    path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def test_promotion_config_parser():
    config = parse_promotion_config(DEFAULT_CONFIG_PATH)

    assert config["source_dataset_version"] == "dataset_v2"
    assert config["target_dataset_version"] == "dataset_v3"
    assert config["require_human_review"] is True


def test_dry_run_does_not_create_target_file(tmp_path):
    target_version = "dataset_test_dry_run"
    config_path = write_config(tmp_path, target_dataset_version=target_version)
    target_path = DATASETS_DIR / f"{target_version}_metadata.json"

    result = subprocess.run(
        [sys.executable, "scripts/promote_dataset_version.py", "--dry-run", "--config", str(config_path)],
        cwd=BACKEND_DIR,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    assert "Dry-run" in result.stdout
    assert not target_path.exists()


def test_target_version_duplicate_returns_error(tmp_path):
    config_path = write_config(tmp_path, target_dataset_version="dataset_v2")
    config = parse_promotion_config(config_path)

    with pytest.raises(ValueError, match="không được trùng"):
        validate_dataset_promotion(config, datasets_dir=DATASETS_DIR, root_dir=ROOT_DIR)


def test_include_beta_missing_path_returns_error(tmp_path):
    config_path = write_config(
        tmp_path,
        target_dataset_version="dataset_test_missing_beta",
        include_beta=True,
        beta_source_path="docs/datasets/beta/missing_file.json",
        minimum_beta_cases=1,
    )
    config = parse_promotion_config(config_path)

    with pytest.raises(ValueError, match="Không tìm thấy beta_source_path"):
        validate_dataset_promotion(config, datasets_dir=DATASETS_DIR, root_dir=ROOT_DIR)


def test_missing_human_review_metadata_returns_error(tmp_path):
    beta_path = tmp_path / "beta_cases.json"
    beta_path.write_text(
        json.dumps(
            {
                "cases": [
                    {
                        "case_id": "BETA001",
                        "role_family": "backend",
                        "expected_label": "medium",
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    config_path = write_config(
        tmp_path,
        target_dataset_version="dataset_test_missing_review",
        include_beta=True,
        beta_source_path=str(beta_path),
        minimum_beta_cases=1,
        require_human_review=True,
    )
    config = parse_promotion_config(config_path)

    with pytest.raises(ValueError, match="thiếu human review metadata"):
        validate_dataset_promotion(config, datasets_dir=DATASETS_DIR, root_dir=ROOT_DIR)
