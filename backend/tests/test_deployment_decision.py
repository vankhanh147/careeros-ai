import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.ml.model_comparison import (
    build_decision_record,
    compare_candidate_with_baseline,
    validate_decision_record,
)
from scripts.create_deployment_decision import BASELINE, create_decision


def write_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def candidate_fixture(tmp_path: Path, *, accuracy=0.85, macro_f1=0.84):
    evaluation_path = tmp_path / "evaluation.json"
    evaluation = {
        "model_version": "candidate_v1",
        "metrics": {"accuracy": accuracy, "macro_f1": macro_f1},
        "benchmark_results": {"U01-U10": {"status": "completed"}},
        "known_limitations": ["Chưa có real beta labels."],
    }
    write_json(evaluation_path, evaluation)
    registry_path = tmp_path / "candidate_v1.json"
    candidate = {
        "model_name": "matching_candidate",
        "model_version": "candidate_v1",
        "dataset_version": "dataset_v3",
        "dataset_hash": "hash-v3",
        "feature_version": "hybrid_features_v1",
        "accuracy": accuracy,
        "macro_f1": macro_f1,
        "artifact_paths": {"evaluation_report": str(evaluation_path)},
        "status": "candidate",
        "production_safe": False,
        "review_history": [{"outcome": "PASS"}],
    }
    write_json(registry_path, candidate)
    return registry_path, candidate, evaluation


def test_no_candidate_keeps_baseline():
    comparison = compare_candidate_with_baseline(
        candidate=None,
        evaluation=None,
        review_result=None,
        baseline=BASELINE,
    )
    assert comparison["comparison_status"] == "inconclusive"
    assert comparison["recommendation"] == "keep_baseline"


def test_good_candidate_can_be_approved_or_kept_shadow(tmp_path):
    _, candidate, evaluation = candidate_fixture(tmp_path)
    comparison = compare_candidate_with_baseline(
        candidate=candidate,
        evaluation=evaluation,
        review_result={"outcome": "PASS"},
        baseline=BASELINE,
    )
    assert comparison["comparison_status"] == "better"
    assert comparison["recommendation"] in {"approve_candidate", "keep_shadow"}


def test_low_candidate_is_rejected(tmp_path):
    _, candidate, evaluation = candidate_fixture(tmp_path, accuracy=0.4, macro_f1=0.45)
    comparison = compare_candidate_with_baseline(
        candidate=candidate,
        evaluation=evaluation,
        review_result={"outcome": "PASS"},
        baseline=BASELINE,
    )
    assert comparison["comparison_status"] == "worse"
    assert comparison["recommendation"] == "reject_candidate"


def test_production_change_true_is_rejected():
    comparison = compare_candidate_with_baseline(
        candidate=None,
        evaluation=None,
        review_result=None,
        baseline=BASELINE,
    )
    record = build_decision_record(
        comparison=comparison,
        candidate=None,
        reviewer="reviewer-test",
        decision_id="decision-test",
    )
    record["production_change_allowed"] = True
    with pytest.raises(ValueError, match="production_change_allowed=false"):
        validate_decision_record(record, allow_no_candidate=True)


def test_candidate_without_candidate_status_fails(tmp_path):
    _, candidate, evaluation = candidate_fixture(tmp_path)
    candidate["status"] = "draft"
    with pytest.raises(ValueError, match="status=candidate"):
        compare_candidate_with_baseline(
            candidate=candidate,
            evaluation=evaluation,
            review_result={"outcome": "PASS"},
            baseline=BASELINE,
        )


def test_candidate_missing_dataset_hash_fails(tmp_path):
    _, candidate, evaluation = candidate_fixture(tmp_path)
    candidate["dataset_hash"] = ""
    with pytest.raises(ValueError, match="dataset_hash"):
        compare_candidate_with_baseline(
            candidate=candidate,
            evaluation=evaluation,
            review_result={"outcome": "PASS"},
            baseline=BASELINE,
        )


def test_dry_run_does_not_write_file(tmp_path, monkeypatch):
    config_path = tmp_path / "review_config.json"
    missing_registry = tmp_path / "missing.json"
    write_json(
        config_path,
        {
            "registry_path": str(missing_registry),
            "dataset_manifest_path": "unused.json",
            "minimum_accuracy": 0.7,
            "minimum_macro_f1": 0.7,
            "warning_margin": 0.05,
            "benchmark_required": True,
            "required_evaluation_fields": [],
        },
    )
    monkeypatch.setattr("scripts.create_deployment_decision.REVIEW_CONFIG_PATH", config_path)
    decisions_dir = tmp_path / "decisions"
    result = create_decision(
        workspace=tmp_path,
        decisions_dir=decisions_dir,
        dry_run=True,
        now=datetime(2026, 6, 27, tzinfo=timezone.utc),
    )
    assert result["record"]["decision"] == "keep_baseline"
    assert result["written"] is False
    assert not decisions_dir.exists()



def test_no_candidate_write_mode_fails(tmp_path, monkeypatch):
    config_path = tmp_path / "review_config.json"
    write_json(
        config_path,
        {
            "registry_path": str(tmp_path / "missing.json"),
            "dataset_manifest_path": "unused.json",
            "minimum_accuracy": 0.7,
            "minimum_macro_f1": 0.7,
            "warning_margin": 0.05,
            "benchmark_required": True,
            "required_evaluation_fields": [],
        },
    )
    monkeypatch.setattr("scripts.create_deployment_decision.REVIEW_CONFIG_PATH", config_path)
    with pytest.raises(ValueError, match="model candidate"):
        create_decision(
            workspace=tmp_path,
            reviewer="founder-review",
            decisions_dir=tmp_path / "decisions",
            dry_run=False,
        )

def test_write_mode_creates_decision_record(tmp_path, monkeypatch):
    registry_path, _, _ = candidate_fixture(tmp_path)
    config_path = tmp_path / "review_config.json"
    write_json(
        config_path,
        {
            "registry_path": str(registry_path),
            "dataset_manifest_path": "unused.json",
            "minimum_accuracy": 0.7,
            "minimum_macro_f1": 0.7,
            "warning_margin": 0.05,
            "benchmark_required": True,
            "required_evaluation_fields": [],
        },
    )
    monkeypatch.setattr("scripts.create_deployment_decision.REVIEW_CONFIG_PATH", config_path)
    decisions_dir = tmp_path / "decisions"
    result = create_decision(
        workspace=tmp_path,
        registry_path=registry_path,
        reviewer="founder-review",
        decisions_dir=decisions_dir,
        dry_run=False,
        now=datetime(2026, 6, 27, tzinfo=timezone.utc),
    )
    output = Path(result["output_path"])
    assert output.exists()
    record = json.loads(output.read_text(encoding="utf-8"))
    assert record["reviewer"] == "founder-review"
    assert record["production_change_allowed"] is False


def test_write_mode_requires_reviewer(tmp_path, monkeypatch):
    registry_path, _, _ = candidate_fixture(tmp_path)
    config_path = tmp_path / "review_config.json"
    write_json(
        config_path,
        {
            "registry_path": str(registry_path),
            "dataset_manifest_path": "unused.json",
            "minimum_accuracy": 0.7,
            "minimum_macro_f1": 0.7,
            "warning_margin": 0.05,
            "benchmark_required": True,
            "required_evaluation_fields": [],
        },
    )
    monkeypatch.setattr("scripts.create_deployment_decision.REVIEW_CONFIG_PATH", config_path)
    with pytest.raises(ValueError, match="reviewer"):
        create_decision(
            workspace=tmp_path,
            registry_path=registry_path,
            reviewer="",
            decisions_dir=tmp_path / "decisions",
            dry_run=False,
        )
