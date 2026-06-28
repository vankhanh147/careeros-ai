import json
from pathlib import Path

from app.ml.shadow_harness import evaluate_shadow_cases, load_training_cases
from scripts.run_shadow_harness import run_shadow_harness


def write_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def sample_dataset():
    return {
        "dataset_version": "dataset_test",
        "cases": [
            {"case_id": "T01", "source": "synthetic", "fit_label": "good"},
            {"case_id": "T02", "source": "benchmark", "fit_label": "weak"},
            {"case_id": "T03", "source": "synthetic", "fit_label": "medium"},
        ],
    }


def rule_predictor(case):
    rows = {
        "T01": {"rule_based_score": 82, "hybrid_score_candidate": 80},
        "T02": {"rule_based_score": 32, "hybrid_score_candidate": 35},
        "T03": {"rule_based_score": 55, "hybrid_score_candidate": 52},
    }
    return rows[case["case_id"]]


def candidate_predictor(case):
    rows = {
        "T01": {"predicted_label": "good", "confidence": 0.9},
        "T02": {"predicted_label": "medium", "confidence": 0.7},
        "T03": {"predicted_label": "medium", "confidence": 0.8},
    }
    return rows[case["case_id"]]


def test_baseline_only():
    dataset = sample_dataset()
    report = evaluate_shadow_cases(
        dataset_metadata=dataset,
        cases=dataset["cases"],
        rule_predictor=rule_predictor,
        candidate_predictor=None,
        candidate_metadata={"available": False, "status": "not_found"},
    )
    assert report["status"] == "baseline_only"
    assert report["recommendation"] == "keep baseline"
    assert report["agreement_rate"] is None
    assert all(record["ml_label"] is None for record in report["comparison_records"])


def test_candidate_available():
    dataset = sample_dataset()
    report = evaluate_shadow_cases(
        dataset_metadata=dataset,
        cases=dataset["cases"],
        rule_predictor=rule_predictor,
        candidate_predictor=candidate_predictor,
        candidate_metadata={"available": True, "status": "candidate", "model_version": "candidate_v1"},
    )
    assert report["status"] == "completed"
    assert report["candidate"]["model_version"] == "candidate_v1"
    assert report["average_confidence"] == 0.8
    assert report["production_change_allowed"] is False


def test_disagreement_summary():
    dataset = sample_dataset()
    report = evaluate_shadow_cases(
        dataset_metadata=dataset,
        cases=dataset["cases"],
        rule_predictor=rule_predictor,
        candidate_predictor=candidate_predictor,
    )
    assert report["agreement_count"] == 2
    assert report["disagreement_count"] == 1
    assert report["rule_better"] == 1
    assert report["candidate_better"] == 0
    assert report["inconclusive"] == 2
    assert report["review_required_count"] == 1
    assert report["confusion_summary"]["weak->medium"] == 1


def test_report_generation_contains_no_raw_text():
    dataset = sample_dataset()
    report = evaluate_shadow_cases(
        dataset_metadata=dataset,
        cases=dataset["cases"],
        rule_predictor=rule_predictor,
        candidate_predictor=candidate_predictor,
    )
    serialized = json.dumps(report, ensure_ascii=False)
    assert "resume_summary" not in serialized
    assert "job_description_summary" not in serialized
    assert report["stored_raw_text"] is False
    assert report["benchmark_cases"] == 1


def test_dry_run_does_not_write(tmp_path):
    dataset_path = tmp_path / "dataset.json"
    config_path = tmp_path / "config.json"
    output_path = tmp_path / "shadow_summary.json"
    write_json(dataset_path, sample_dataset())
    write_json(
        config_path,
        {
            "enabled": False,
            "candidate_model_version": "",
            "candidate_registry_path": "",
            "mode": "disabled",
            "sample_rate": 0.0,
            "max_latency_ms": 200,
            "log_disagreements_only": True,
            "store_raw_text": False,
            "production_score_source": "rule_based",
            "allow_user_facing_output": False,
        },
    )
    result = run_shadow_harness(
        dataset_path=dataset_path,
        config_path=config_path,
        output_path=output_path,
        workspace=tmp_path,
        dry_run=True,
    )
    assert result["written"] is False
    assert not output_path.exists()
    assert result["report"]["status"] == "baseline_only"


def test_no_candidate_registry_does_not_crash(tmp_path):
    predictor, metadata = __import__(
        "app.ml.shadow_harness", fromlist=["load_candidate_predictor"]
    ).load_candidate_predictor(
        registry_path=tmp_path / "missing.json",
        workspace=tmp_path,
    )
    assert predictor is None
    assert metadata["available"] is False
    assert metadata["status"] == "not_found"


def test_load_training_cases(tmp_path):
    path = tmp_path / "dataset.json"
    write_json(path, sample_dataset())
    metadata, cases = load_training_cases(path)
    assert metadata["dataset_version"] == "dataset_test"
    assert len(cases) == 3
