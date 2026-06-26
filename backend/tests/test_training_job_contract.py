import json
from pathlib import Path

import pytest

from scripts.run_training_job import (
    calculate_artifact_hash,
    load_training_job_config,
    run_training_job,
    validate_dataset_contract,
)


def write_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def sample_cases():
    labels = ["good", "medium", "weak", "mismatch"] * 3
    cases = []
    for index, label in enumerate(labels, start=1):
        cases.append(
            {
                "case_id": f"T{index:03d}",
                "resume_summary": f"CV thử nghiệm có backend, API và project #{index}.",
                "job_description_summary": f"JD thử nghiệm cần backend, API và kỹ năng phù hợp #{index}.",
                "target_role": "Backend Developer",
                "role_family": "backend",
                "candidate_stack": "Python",
                "jd_stack": "FastAPI",
                "skill_overlap": ["Python"],
                "missing_critical_skills": ["Docker"] if label != "good" else [],
                "fit_label": label,
            }
        )
    return cases


def make_contract_files(tmp_path: Path, *, model_version: str = "contract_test_model_v1"):
    config = {
        "config_id": "test_training_config",
        "dataset_version": "dataset_v3",
        "feature_version": "hybrid_features_v1",
        "classifier": "LogisticRegression",
        "model_name": "contract_test_model",
        "model_version": model_version,
        "random_seed": 42,
        "split_ratio": {"train": 0.75, "test": 0.25},
    }
    dataset = {
        "schema_version": "careeros-training-dataset-v1",
        "dataset_version": "dataset_v3",
        "case_count": 12,
        "sources": {"synthetic": 12, "benchmark": 0, "beta": 0},
        "cases": sample_cases(),
    }
    manifest = {
        "dataset_version": "dataset_v3",
        "artifact_name": "training_dataset_v3.json",
        "artifact_hash": calculate_artifact_hash(dataset),
        "total_cases": 12,
    }
    config_path = tmp_path / "config.json"
    dataset_path = tmp_path / "training_dataset_v3.json"
    manifest_path = tmp_path / "training_dataset_manifest.json"
    write_json(config_path, config)
    write_json(dataset_path, dataset)
    write_json(manifest_path, manifest)
    return config_path, dataset_path, manifest_path, config, dataset, manifest


def test_load_training_config(tmp_path):
    config_path, *_ = make_contract_files(tmp_path)

    config = load_training_job_config(config_path)

    assert config["dataset_version"] == "dataset_v3"
    assert config["model_version"] == "contract_test_model_v1"


def test_validate_dataset_hash(tmp_path):
    _, _, _, config, dataset, manifest = make_contract_files(tmp_path)

    validate_dataset_contract(
        config=config,
        dataset=dataset,
        manifest=manifest,
        registry_dir=tmp_path / "registry_ok",
        models_dir=tmp_path / "models_ok",
    )


def test_hash_mismatch_fails(tmp_path):
    _, _, _, config, dataset, manifest = make_contract_files(tmp_path)
    manifest["artifact_hash"] = "broken"

    with pytest.raises(ValueError, match="artifact_hash"):
        validate_dataset_contract(
            config=config,
            dataset=dataset,
            manifest=manifest,
            registry_dir=tmp_path / "registry_hash_fail",
            models_dir=tmp_path / "models_hash_fail",
        )


def test_duplicate_model_version_fails(tmp_path):
    _, _, _, config, dataset, manifest = make_contract_files(tmp_path)
    registry_dir = tmp_path / "registry"
    write_json(registry_dir / "contract_test_model_v1.json", {"model_version": "contract_test_model_v1"})

    with pytest.raises(ValueError, match="model_version đã tồn tại"):
        validate_dataset_contract(
            config=config,
            dataset=dataset,
            manifest=manifest,
            registry_dir=registry_dir,
            models_dir=tmp_path / "models",
        )


def test_training_job_dry_run_does_not_write_artifacts(tmp_path):
    config_path, dataset_path, manifest_path, *_ = make_contract_files(tmp_path)
    models_dir = tmp_path / "models"

    result = run_training_job(
        config_path=config_path,
        dataset_path=dataset_path,
        manifest_path=manifest_path,
        models_dir=models_dir,
        experiments_dir=tmp_path / "experiments",
        registry_dir=tmp_path / "registry",
        reports_dir=tmp_path / "reports",
        dry_run=True,
    )

    assert result["ok"] is True
    assert result["dry_run"] is True
    assert result["metadata"]["status"] == "dry_run"
    assert not models_dir.exists()


def test_training_job_real_run_outputs_metadata(tmp_path):
    config_path, dataset_path, manifest_path, *_ = make_contract_files(tmp_path, model_version="contract_test_model_v2")

    result = run_training_job(
        config_path=config_path,
        dataset_path=dataset_path,
        manifest_path=manifest_path,
        models_dir=tmp_path / "models",
        experiments_dir=tmp_path / "experiments",
        registry_dir=tmp_path / "registry",
        reports_dir=tmp_path / "reports",
        dry_run=False,
    )

    metadata = result["metadata"]
    assert metadata["status"] == "completed"
    assert metadata["production_safe"] is False
    assert {"run_id", "dataset_version", "dataset_hash", "feature_version", "model_name", "model_version"}.issubset(
        metadata
    )
    assert Path(metadata["artifact_paths"]["model"]).exists()
    assert Path(metadata["artifact_paths"]["registry"]).exists()
