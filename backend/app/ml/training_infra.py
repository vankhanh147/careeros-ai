"""Helpers for offline ML training infrastructure metadata.

The functions in this module only parse and validate local JSON metadata used
by the training workspace. They do not touch production scoring or runtime
prediction behavior.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_DATASET_FIELDS = {
    "dataset_id",
    "version",
    "created_at",
    "source",
    "total_cases",
    "synthetic_cases",
    "benchmark_cases",
    "beta_cases",
    "notes",
}

REQUIRED_MODEL_FIELDS = {
    "model_name",
    "model_version",
    "dataset_version",
    "feature_version",
    "accuracy",
    "macro_f1",
    "created_at",
    "training_command",
}

REQUIRED_EXPERIMENT_FIELDS = {
    "experiment_id",
    "model",
    "dataset",
    "metrics",
    "notes",
    "status",
}

REQUIRED_TRAINING_CONFIG_FIELDS = {
    "random_seed",
    "split_ratio",
    "feature_version",
    "classifier",
    "dataset_version",
}


def load_json_metadata(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError("Metadata phải là JSON object.")
    return payload


def parse_dataset_metadata(path: str | Path) -> dict[str, Any]:
    metadata = load_json_metadata(path)
    _require_fields(metadata, REQUIRED_DATASET_FIELDS, "dataset metadata")
    _require_non_negative_int(metadata, "total_cases")
    _require_non_negative_int(metadata, "synthetic_cases")
    _require_non_negative_int(metadata, "benchmark_cases")
    _require_non_negative_int(metadata, "beta_cases")
    counted_cases = metadata["synthetic_cases"] + metadata["benchmark_cases"] + metadata["beta_cases"]
    if counted_cases > metadata["total_cases"]:
        raise ValueError("Tổng synthetic/benchmark/beta cases không được lớn hơn total_cases.")
    return metadata


def parse_model_metadata(path: str | Path) -> dict[str, Any]:
    metadata = load_json_metadata(path)
    _require_fields(metadata, REQUIRED_MODEL_FIELDS, "model metadata")
    _require_score(metadata, "accuracy")
    _require_score(metadata, "macro_f1")
    return metadata


def parse_experiment_metadata(path: str | Path) -> dict[str, Any]:
    metadata = load_json_metadata(path)
    _require_fields(metadata, REQUIRED_EXPERIMENT_FIELDS, "experiment metadata")
    if not isinstance(metadata["metrics"], dict):
        raise ValueError("experiment.metrics phải là JSON object.")
    return metadata


def parse_training_config(path: str | Path) -> dict[str, Any]:
    config = load_json_metadata(path)
    _require_fields(config, REQUIRED_TRAINING_CONFIG_FIELDS, "training config")
    _require_non_negative_int(config, "random_seed")
    split_ratio = config["split_ratio"]
    if not isinstance(split_ratio, dict):
        raise ValueError("split_ratio phải là JSON object.")
    train = split_ratio.get("train")
    test = split_ratio.get("test")
    if not isinstance(train, (int, float)) or not isinstance(test, (int, float)):
        raise ValueError("split_ratio.train và split_ratio.test phải là số.")
    if round(float(train) + float(test), 5) != 1.0:
        raise ValueError("split_ratio.train + split_ratio.test phải bằng 1.0.")
    return config


def _require_fields(payload: dict[str, Any], fields: set[str], label: str) -> None:
    missing = sorted(field for field in fields if field not in payload)
    if missing:
        raise ValueError(f"{label} thiếu field bắt buộc: {', '.join(missing)}")


def _require_non_negative_int(payload: dict[str, Any], field: str) -> None:
    value = payload[field]
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"{field} phải là số nguyên không âm.")


def _require_score(payload: dict[str, Any], field: str) -> None:
    value = payload[field]
    if not isinstance(value, (int, float)) or not 0 <= float(value) <= 1:
        raise ValueError(f"{field} phải nằm trong khoảng 0..1.")
