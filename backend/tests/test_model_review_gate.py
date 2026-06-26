import json
from pathlib import Path

from app.ml.model_review import apply_review_result, load_model_review_config, review_registry
from scripts.review_model_registry import run_review


def write_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def make_review_fixture(
    tmp_path: Path,
    *,
    accuracy=0.82,
    macro_f1=0.8,
    include_evaluation=True,
    dataset_hash="hash-ok",
    manifest_hash="hash-ok",
):
    workspace = tmp_path
    registry_dir = workspace / "backend/ml/registry"
    model_dir = workspace / "backend/ml/models/model_v1"
    experiment_path = workspace / "backend/ml/experiments/run_v1.json"
    evaluation_path = workspace / "backend/ml/reports/run_v1_evaluation.json"
    manifest_path = workspace / "backend/ml/datasets/training_dataset_manifest.json"
    for name in ("model.joblib", "vectorizer.joblib", "labels.json", "model_metadata.json"):
        target = model_dir / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("artifact", encoding="utf-8")
    metrics = {
        "accuracy": accuracy,
        "macro_f1": macro_f1,
        "classification_report": {},
        "confusion_matrix": [],
    }
    experiment = {
        "model_version": "model_v1",
        "dataset_hash": dataset_hash,
        "metrics": metrics,
    }
    evaluation = {
        "model_version": "model_v1",
        "dataset_hash": dataset_hash,
        "metrics": metrics,
        "benchmark_results": {"U01-U10": "completed"},
    }
    write_json(experiment_path, experiment)
    if include_evaluation:
        write_json(evaluation_path, evaluation)
    write_json(manifest_path, {"dataset_version": "dataset_v3", "artifact_hash": manifest_hash})
    registry_path = registry_dir / "model_v1.json"
    registry = {
        "model_name": "matching_model",
        "model_version": "model_v1",
        "dataset_version": "dataset_v3",
        "dataset_hash": dataset_hash,
        "feature_version": "hybrid_features_v1",
        "accuracy": accuracy,
        "macro_f1": macro_f1,
        "artifact_paths": {
            "model": str(model_dir / "model.joblib"),
            "vectorizer": str(model_dir / "vectorizer.joblib"),
            "labels": str(model_dir / "labels.json"),
            "model_metadata": str(model_dir / "model_metadata.json"),
            "experiment": str(experiment_path),
            "registry": str(registry_path),
            "evaluation_report": str(evaluation_path),
        },
        "status": "draft",
        "production_safe": False,
    }
    write_json(registry_path, registry)
    config = {
        "registry_path": str(registry_path),
        "dataset_manifest_path": str(manifest_path),
        "minimum_accuracy": 0.7,
        "minimum_macro_f1": 0.7,
        "warning_margin": 0.05,
        "benchmark_required": True,
        "required_evaluation_fields": [
            "accuracy",
            "macro_f1",
            "classification_report",
            "confusion_matrix",
        ],
    }
    config_path = workspace / "backend/ml/configs/model_review_config.json"
    write_json(config_path, config)
    return workspace, registry_path, registry_dir, config_path, config


def test_review_pass(tmp_path):
    workspace, registry_path, registry_dir, _, config = make_review_fixture(tmp_path)
    result = review_registry(
        registry_path=registry_path,
        config=config,
        workspace=workspace,
        registry_dir=registry_dir,
    )
    assert result["outcome"] == "PASS"
    assert result["target_status"] == "candidate"


def test_review_warning_near_threshold(tmp_path):
    workspace, registry_path, registry_dir, _, config = make_review_fixture(
        tmp_path, accuracy=0.68, macro_f1=0.68
    )
    result = review_registry(
        registry_path=registry_path,
        config=config,
        workspace=workspace,
        registry_dir=registry_dir,
    )
    assert result["outcome"] == "WARNING"
    assert result["target_status"] == "candidate"


def test_review_fail_below_threshold(tmp_path):
    workspace, registry_path, registry_dir, _, config = make_review_fixture(
        tmp_path, accuracy=0.4, macro_f1=0.4
    )
    result = review_registry(
        registry_path=registry_path,
        config=config,
        workspace=workspace,
        registry_dir=registry_dir,
    )
    assert result["outcome"] == "FAIL"
    assert result["target_status"] == "rejected"


def test_missing_artifact_fails(tmp_path):
    workspace, registry_path, registry_dir, _, config = make_review_fixture(tmp_path)
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    Path(registry["artifact_paths"]["model"]).unlink()
    result = review_registry(
        registry_path=registry_path,
        config=config,
        workspace=workspace,
        registry_dir=registry_dir,
    )
    assert result["outcome"] == "FAIL"
    assert any(issue["code"] == "MODEL_NOT_FOUND" for issue in result["issues"])


def test_hash_mismatch_fails(tmp_path):
    workspace, registry_path, registry_dir, _, config = make_review_fixture(
        tmp_path, manifest_hash="hash-other"
    )
    result = review_registry(
        registry_path=registry_path,
        config=config,
        workspace=workspace,
        registry_dir=registry_dir,
    )
    assert any(issue["code"] == "DATASET_HASH_MISMATCH" for issue in result["issues"])


def test_missing_evaluation_fails(tmp_path):
    workspace, registry_path, registry_dir, _, config = make_review_fixture(
        tmp_path, include_evaluation=False
    )
    result = review_registry(
        registry_path=registry_path,
        config=config,
        workspace=workspace,
        registry_dir=registry_dir,
    )
    assert result["outcome"] == "FAIL"
    assert any(issue["code"] == "EVALUATION_REPORT_NOT_FOUND" for issue in result["issues"])


def test_duplicate_registry_fails(tmp_path):
    workspace, registry_path, registry_dir, _, config = make_review_fixture(tmp_path)
    duplicate = json.loads(registry_path.read_text(encoding="utf-8"))
    write_json(registry_dir / "duplicate.json", duplicate)
    result = review_registry(
        registry_path=registry_path,
        config=config,
        workspace=workspace,
        registry_dir=registry_dir,
    )
    assert any(issue["code"] == "DUPLICATE_REGISTRY" for issue in result["issues"])


def test_candidate_promotion_keeps_production_safe_false(tmp_path):
    workspace, registry_path, registry_dir, _, config = make_review_fixture(tmp_path)
    result = review_registry(
        registry_path=registry_path,
        config=config,
        workspace=workspace,
        registry_dir=registry_dir,
    )
    updated = apply_review_result(registry_path, result)
    assert updated["status"] == "candidate"
    assert updated["production_safe"] is False
    assert updated["review_history"]


def test_dry_run_does_not_update_registry(tmp_path):
    workspace, registry_path, _, config_path, _ = make_review_fixture(tmp_path)
    before = registry_path.read_text(encoding="utf-8")
    result = run_review(
        config_path=config_path,
        workspace=workspace,
        registry_path=registry_path,
        dry_run=True,
    )
    assert result["outcome"] == "PASS"
    assert result["registry_updated"] is False
    assert registry_path.read_text(encoding="utf-8") == before


def test_load_review_config(tmp_path):
    _, _, _, config_path, _ = make_review_fixture(tmp_path)
    config = load_model_review_config(config_path)
    assert config["minimum_accuracy"] == 0.7
