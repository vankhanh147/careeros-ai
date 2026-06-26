import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.ml.release_audit import (
    REQUIRED_CHECKS,
    build_release_audit,
    calculate_artifact_hash,
    summarize_checklist,
    validate_audit_record,
    validate_checklist,
)


def write_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def make_audit_fixture(tmp_path: Path, *, warning=False, missing_model=False):
    dataset = {
        "dataset_version": "dataset_v3",
        "cases": [
            {
                "case_id": "SYN001",
                "fit_label": "good",
                "source": "synthetic",
                "resume_summary": "Backend Python",
            }
        ],
    }
    dataset_path = tmp_path / "backend/ml/datasets/training_dataset_v3.json"
    manifest_path = tmp_path / "backend/ml/datasets/training_dataset_manifest.json"
    config_path = tmp_path / "backend/ml/configs/training_config.json"
    write_json(dataset_path, dataset)
    write_json(
        manifest_path,
        {
            "dataset_version": "dataset_v3",
            "artifact_hash": calculate_artifact_hash(dataset),
            "beta_count": 0 if warning else 1,
        },
    )
    if not warning:
        dataset["cases"].append(
            {
                "case_id": "BETA001",
                "fit_label": "medium",
                "source": "beta",
                "approved_for_training": True,
                "anonymized": True,
            }
        )
        write_json(dataset_path, dataset)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["artifact_hash"] = calculate_artifact_hash(dataset)
        write_json(manifest_path, manifest)
    write_json(config_path, {"dataset_version": "dataset_v3"})

    model_dir = tmp_path / "backend/ml/models/candidate_v1"
    model_path = model_dir / "model.joblib"
    metadata_path = model_dir / "model_metadata.json"
    experiment_path = tmp_path / "backend/ml/experiments/run_v1.json"
    evaluation_path = tmp_path / "backend/ml/reports/run_v1_evaluation.json"
    if not missing_model:
        model_path.parent.mkdir(parents=True, exist_ok=True)
        model_path.write_bytes(b"model")
    write_json(metadata_path, {"model_version": "candidate_v1"})
    write_json(experiment_path, {"model_version": "candidate_v1"})
    write_json(
        evaluation_path,
        {
            "model_version": "candidate_v1",
            "benchmark_results": {"U01-U10": "completed"},
            "metrics": {"accuracy": 0.85, "macro_f1": 0.84},
        },
    )
    registry_path = tmp_path / "backend/ml/registry/candidate_v1.json"
    registry = {
        "model_version": "candidate_v1",
        "dataset_version": "dataset_v3",
        "dataset_hash": calculate_artifact_hash(dataset),
        "status": "candidate",
        "production_safe": False,
        "review_history": [{"outcome": "PASS"}],
        "artifact_paths": {
            "model": str(model_path),
            "model_metadata": str(metadata_path),
            "experiment": str(experiment_path),
            "evaluation_report": str(evaluation_path),
        },
    }
    write_json(registry_path, registry)
    decision_path = tmp_path / "backend/ml/decisions/decision_v1.json"
    write_json(
        decision_path,
        {
            "decision_id": "decision_v1",
            "candidate_model_version": "candidate_v1",
            "risk_level": "low",
            "decision": "approve_candidate",
            "production_change_allowed": False,
        },
    )
    return {
        "workspace": tmp_path,
        "manifest": manifest_path,
        "dataset": dataset_path,
        "config": config_path,
        "registry": registry_path,
        "decision": decision_path,
    }


def build_fixture_audit(paths, *, quality=None):
    return build_release_audit(
        workspace=paths["workspace"],
        manifest_path=paths["manifest"],
        dataset_path=paths["dataset"],
        training_config_path=paths["config"],
        registry_path=paths["registry"],
        decision_path=paths["decision"],
        quality_evidence=quality or {"pytest": True, "compileall": True, "pip_check": True},
        reviewer="reviewer-test",
        audit_id="audit-test",
    )


def test_release_audit_pass(tmp_path):
    record = build_fixture_audit(make_audit_fixture(tmp_path))
    assert record["checklist_summary"]["outcome"] == "PASS"
    assert record["passed"] is True


def test_release_audit_warning(tmp_path):
    record = build_fixture_audit(make_audit_fixture(tmp_path, warning=True))
    assert record["checklist_summary"]["outcome"] == "WARNING"
    assert record["passed"] is False


def test_release_audit_fail_missing_artifact(tmp_path):
    record = build_fixture_audit(make_audit_fixture(tmp_path, missing_model=True))
    assert record["checklist_summary"]["outcome"] == "FAIL"
    assert any(
        item["check_id"] == "model_artifact" and item["status"] == "FAIL"
        for item in record["checklist_result"]
    )


def test_checklist_incomplete_fails():
    with pytest.raises(ValueError, match="thiếu mục bắt buộc"):
        validate_checklist([])


def test_production_change_true_fails(tmp_path):
    record = build_fixture_audit(make_audit_fixture(tmp_path))
    record["production_change_allowed"] = True
    with pytest.raises(ValueError, match="production_change_allowed=false"):
        validate_audit_record(record)


def test_dry_run_does_not_write(tmp_path, monkeypatch):
    from scripts import run_release_audit as script

    paths = make_audit_fixture(tmp_path)
    review_config = tmp_path / "review_config.json"
    write_json(
        review_config,
        {
            "registry_path": str(paths["registry"]),
            "dataset_manifest_path": str(paths["manifest"]),
            "minimum_accuracy": 0.7,
            "minimum_macro_f1": 0.7,
            "warning_margin": 0.05,
            "benchmark_required": True,
            "required_evaluation_fields": [],
        },
    )
    monkeypatch.setattr(script, "REVIEW_CONFIG_PATH", review_config)
    monkeypatch.setattr(script, "MANIFEST_PATH", paths["manifest"])
    monkeypatch.setattr(script, "DATASET_PATH", paths["dataset"])
    monkeypatch.setattr(script, "TRAINING_CONFIG_PATH", paths["config"])
    monkeypatch.setattr(script, "DECISIONS_DIR", paths["decision"].parent)
    output_dir = tmp_path / "audits"
    result = script.run_audit(
        workspace=tmp_path,
        registry_path=paths["registry"],
        decision_path=paths["decision"],
        reviewer="",
        audits_dir=output_dir,
        dry_run=True,
        now=datetime(2026, 6, 27, tzinfo=timezone.utc),
    )
    assert result["written"] is False
    assert not output_dir.exists()


def test_write_mode_creates_audit(tmp_path, monkeypatch):
    from scripts import run_release_audit as script

    paths = make_audit_fixture(tmp_path)
    review_config = tmp_path / "review_config.json"
    write_json(
        review_config,
        {
            "registry_path": str(paths["registry"]),
            "dataset_manifest_path": str(paths["manifest"]),
            "minimum_accuracy": 0.7,
            "minimum_macro_f1": 0.7,
            "warning_margin": 0.05,
            "benchmark_required": True,
            "required_evaluation_fields": [],
        },
    )
    quality_path = tmp_path / "quality.json"
    write_json(quality_path, {"pytest": True, "compileall": True, "pip_check": True})
    monkeypatch.setattr(script, "REVIEW_CONFIG_PATH", review_config)
    monkeypatch.setattr(script, "MANIFEST_PATH", paths["manifest"])
    monkeypatch.setattr(script, "DATASET_PATH", paths["dataset"])
    monkeypatch.setattr(script, "TRAINING_CONFIG_PATH", paths["config"])
    monkeypatch.setattr(script, "DECISIONS_DIR", paths["decision"].parent)
    output_dir = tmp_path / "audits"
    result = script.run_audit(
        workspace=tmp_path,
        registry_path=paths["registry"],
        decision_path=paths["decision"],
        quality_evidence_path=quality_path,
        reviewer="founder-review",
        audits_dir=output_dir,
        dry_run=False,
        now=datetime(2026, 6, 27, tzinfo=timezone.utc),
    )
    assert result["written"] is True
    output = Path(result["output_path"])
    assert output.exists()
    assert json.loads(output.read_text(encoding="utf-8"))["production_change_allowed"] is False


def test_required_check_count_is_stable():
    assert len(REQUIRED_CHECKS) == 21
