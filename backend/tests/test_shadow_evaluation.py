import json
from pathlib import Path

import pytest

from app.ml.shadow_evaluation import create_shadow_plan, load_shadow_config, validate_shadow_config
from scripts.plan_shadow_evaluation import plan_shadow_evaluation


def default_config():
    return {
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
    }


def write_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def test_default_config_disabled(tmp_path):
    path = tmp_path / "shadow_config.json"
    write_json(path, default_config())
    config = load_shadow_config(path)
    plan = create_shadow_plan(config=config, workspace=tmp_path)
    assert config["enabled"] is False
    assert plan["effective_enabled"] is False
    assert plan["effective_mode"] == "disabled"
    assert plan["runtime_activation_allowed"] is False


def test_user_facing_output_true_rejected():
    config = default_config()
    config["allow_user_facing_output"] = True
    with pytest.raises(ValueError, match="allow_user_facing_output"):
        validate_shadow_config(config)


def test_store_raw_text_true_rejected():
    config = default_config()
    config["store_raw_text"] = True
    with pytest.raises(ValueError, match="store_raw_text"):
        validate_shadow_config(config)


def test_invalid_sample_rate_rejected():
    config = default_config()
    config["sample_rate"] = 1.1
    with pytest.raises(ValueError, match="sample_rate"):
        validate_shadow_config(config)


def test_shadow_without_candidate_returns_safe_disabled_warning(tmp_path):
    config = default_config()
    config.update(
        {
            "enabled": True,
            "mode": "shadow",
            "sample_rate": 0.1,
            "candidate_model_version": "candidate_v1",
            "candidate_registry_path": "backend/ml/registry/candidate_v1.json",
        }
    )
    plan = create_shadow_plan(config=config, workspace=tmp_path)
    assert plan["effective_enabled"] is False
    assert plan["effective_mode"] == "disabled"
    assert plan["outcome"] == "WARNING"
    assert plan["candidate_status"] == "not_found"


def test_valid_candidate_config_creates_shadow_plan(tmp_path):
    registry_path = tmp_path / "backend/ml/registry/candidate_v1.json"
    write_json(
        registry_path,
        {
            "model_version": "candidate_v1",
            "status": "candidate",
            "production_safe": False,
        },
    )
    config = default_config()
    config.update(
        {
            "enabled": True,
            "mode": "shadow",
            "sample_rate": 0.1,
            "candidate_model_version": "candidate_v1",
            "candidate_registry_path": "backend/ml/registry/candidate_v1.json",
        }
    )
    plan = create_shadow_plan(config=config, workspace=tmp_path)
    assert plan["effective_mode"] == "shadow"
    assert plan["candidate_status"] == "candidate"
    assert plan["outcome"] == "PASS"
    assert plan["effective_enabled"] is False
    assert plan["runtime_activation_allowed"] is False


def test_cli_dry_run_does_not_write_file(tmp_path):
    config_path = tmp_path / "shadow_config.json"
    output_path = tmp_path / "shadow_plan.json"
    write_json(config_path, default_config())
    result = plan_shadow_evaluation(
        config_path=config_path,
        workspace=tmp_path,
        output_path=output_path,
        dry_run=True,
    )
    assert result["written"] is False
    assert not output_path.exists()
