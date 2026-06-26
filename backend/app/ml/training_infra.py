"""Helpers for offline ML training infrastructure metadata.

The functions in this module only parse and validate local JSON metadata used
by the training workspace. They do not touch production scoring or runtime
prediction behavior.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
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


LABEL_REVIEW_STATUSES = {
    "NEW",
    "ANONYMIZED",
    "UNDER_REVIEW",
    "APPROVED",
    "PROMOTED",
    "TRAINABLE",
}

LABEL_REVIEW_TRANSITIONS = {
    "NEW": {"ANONYMIZED"},
    "ANONYMIZED": {"UNDER_REVIEW"},
    "UNDER_REVIEW": {"APPROVED"},
    "APPROVED": {"PROMOTED"},
    "PROMOTED": {"TRAINABLE"},
    "TRAINABLE": set(),
}

TRAINING_APPROVAL_STATUSES = {"APPROVED", "PROMOTED", "TRAINABLE"}

REQUIRED_LABEL_REVIEW_FIELDS = {
    "case_id",
    "dataset_version",
    "review_status",
    "reviewer",
    "review_time",
    "label_confidence",
    "disagreement_reason",
    "notes",
    "approved_for_training",
    "anonymized",
}
REQUIRED_PROMOTION_CONFIG_FIELDS = {
    "source_dataset_version",
    "target_dataset_version",
    "include_synthetic",
    "include_benchmark",
    "include_beta",
    "beta_source_path",
    "minimum_beta_cases",
    "require_human_review",
    "notes",
}

MOJIBAKE_PATTERN = re.compile(
    r"\u00c3|\u00c2|\u00e1\u00ba|\u00e1\u00bb|\u00c4|\u00c6|\u00c5|\ufffd|M\?|Kh\?|H\?\?|tr\?|\?\?\?"
)
EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_PATTERN = re.compile(r"(?<!\d)(?:\+?\d[\d\s().-]{8,}\d)(?!\d)")
ISO_TIMESTAMP_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z?")


def load_json_metadata(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError("Metadata phải là JSON object.")
    return payload


def parse_dataset_metadata(path: str | Path) -> dict[str, Any]:
    return parse_dataset_metadata_dict(load_json_metadata(path))


def parse_dataset_metadata_dict(metadata: dict[str, Any]) -> dict[str, Any]:
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




def parse_label_review_schema(path: str | Path) -> dict[str, Any]:
    schema = load_json_metadata(path)
    required = schema.get("required_fields")
    statuses = schema.get("allowed_statuses")
    if not isinstance(required, list) or not set(REQUIRED_LABEL_REVIEW_FIELDS).issubset(set(required)):
        raise ValueError("label review schema thiếu required_fields bắt buộc.")
    if not isinstance(statuses, list) or set(statuses) != LABEL_REVIEW_STATUSES:
        raise ValueError("label review schema có allowed_statuses không hợp lệ.")
    return schema


def load_label_review_cases(path: str | Path) -> list[dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if isinstance(payload, list):
        cases = payload
    elif isinstance(payload, dict):
        cases = payload.get("cases", [])
    else:
        raise ValueError("Review dataset phải là JSON array hoặc object có field cases.")
    if not isinstance(cases, list):
        raise ValueError("Review dataset field cases phải là list.")
    return [dict(case) for case in cases if isinstance(case, dict)]


def validate_label_review_case(case: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = sorted(field for field in REQUIRED_LABEL_REVIEW_FIELDS if field not in case)
    if missing:
        errors.append(f"Thiếu field bắt buộc: {', '.join(missing)}")
        return errors

    status = str(case["review_status"])
    reviewer = str(case.get("reviewer") or "").strip()
    serialized = json.dumps(case, ensure_ascii=False)

    if status not in LABEL_REVIEW_STATUSES:
        errors.append(f"review_status không hợp lệ: {status}")
    if MOJIBAKE_PATTERN.search(serialized):
        errors.append("Case có dấu hiệu mojibake.")
    pii_scan_text = ISO_TIMESTAMP_PATTERN.sub("", serialized)
    if EMAIL_PATTERN.search(serialized) or PHONE_PATTERN.search(pii_scan_text):
        errors.append("Case có dấu hiệu PII.")
    if not isinstance(case["approved_for_training"], bool):
        errors.append("approved_for_training phải là boolean.")
    if not isinstance(case["anonymized"], bool):
        errors.append("anonymized phải là boolean.")
    if not isinstance(case["label_confidence"], (int, float)) or not 0 <= float(case["label_confidence"]) <= 1:
        errors.append("label_confidence phải nằm trong khoảng 0..1.")
    if status in {"UNDER_REVIEW", "APPROVED", "PROMOTED", "TRAINABLE"} and not reviewer:
        errors.append("reviewer bắt buộc từ trạng thái UNDER_REVIEW trở đi.")
    if status in TRAINING_APPROVAL_STATUSES and case["anonymized"] is not True:
        errors.append("anonymized=true là bắt buộc trước khi APPROVED/PROMOTED/TRAINABLE.")
    if case["approved_for_training"] is True and status not in TRAINING_APPROVAL_STATUSES:
        errors.append("approved_for_training chỉ được true khi status là APPROVED, PROMOTED hoặc TRAINABLE.")
    if case["approved_for_training"] is True and case["anonymized"] is not True:
        errors.append("approved_for_training=true yêu cầu anonymized=true.")

    previous_status = case.get("previous_status")
    if previous_status:
        if previous_status not in LABEL_REVIEW_STATUSES:
            errors.append(f"previous_status không hợp lệ: {previous_status}")
        elif status != previous_status and status not in LABEL_REVIEW_TRANSITIONS[previous_status]:
            errors.append(f"Transition không hợp lệ: {previous_status} -> {status}")

    return errors


def validate_label_review_cases(cases: list[dict[str, Any]]) -> dict[str, Any]:
    case_results: list[dict[str, Any]] = []
    total_errors = 0
    total_warnings = 0
    ready_count = 0

    for index, case in enumerate(cases, start=1):
        errors = validate_label_review_case(case)
        warnings: list[str] = []
        status = str(case.get("review_status", ""))
        if status == "NEW":
            warnings.append("Case mới chưa được ẩn danh hoặc review.")
        if status == "ANONYMIZED" and not str(case.get("reviewer") or "").strip():
            warnings.append("Case đã ẩn danh nhưng chưa có reviewer.")
        ready = not errors and case.get("approved_for_training") is True and status in {"APPROVED", "PROMOTED", "TRAINABLE"}
        if ready:
            ready_count += 1
        total_errors += len(errors)
        total_warnings += len(warnings)
        case_results.append(
            {
                "index": index,
                "case_id": case.get("case_id", f"case_{index}"),
                "review_status": status,
                "errors": errors,
                "warnings": warnings,
                "ready_for_promotion": ready,
            }
        )

    return {
        "total_cases": len(cases),
        "ready_for_promotion_count": ready_count,
        "errors_count": total_errors,
        "warnings_count": total_warnings,
        "ready_for_promotion": total_errors == 0 and ready_count > 0,
        "case_results": case_results,
    }


def validate_label_review_file(path: str | Path) -> dict[str, Any]:
    return validate_label_review_cases(load_label_review_cases(path))


def parse_promotion_config(path: str | Path) -> dict[str, Any]:
    config = load_json_metadata(path)
    _require_fields(config, REQUIRED_PROMOTION_CONFIG_FIELDS, "promotion config")
    _require_bool(config, "include_synthetic")
    _require_bool(config, "include_benchmark")
    _require_bool(config, "include_beta")
    _require_bool(config, "require_human_review")
    _require_non_negative_int(config, "minimum_beta_cases")
    if not str(config["source_dataset_version"]).strip():
        raise ValueError("source_dataset_version không được rỗng.")
    if not str(config["target_dataset_version"]).strip():
        raise ValueError("target_dataset_version không được rỗng.")
    return config


def validate_dataset_promotion(
    config: dict[str, Any],
    *,
    datasets_dir: str | Path,
    root_dir: str | Path,
) -> dict[str, Any]:
    datasets_path = Path(datasets_dir)
    root_path = Path(root_dir)
    source_version = str(config["source_dataset_version"])
    target_version = str(config["target_dataset_version"])
    source_path = datasets_path / f"{source_version}_metadata.json"
    target_path = datasets_path / f"{target_version}_metadata.json"

    if source_version == target_version:
        raise ValueError("target_dataset_version không được trùng source_dataset_version.")
    if not source_path.exists():
        raise ValueError(f"Không tìm thấy source dataset metadata: {source_path}")
    if target_path.exists():
        raise ValueError(f"target_dataset_version đã tồn tại: {target_version}")

    source_metadata = parse_dataset_metadata(source_path)
    beta_cases: list[dict[str, Any]] = []
    beta_source_path = str(config.get("beta_source_path") or "").strip()
    if config["include_beta"]:
        if not beta_source_path:
            raise ValueError("include_beta=true yêu cầu beta_source_path.")
        beta_path = _resolve_path(root_path, beta_source_path)
        if not beta_path.exists():
            raise ValueError(f"Không tìm thấy beta_source_path: {beta_source_path}")
        beta_cases = load_beta_cases(beta_path)
        if len(beta_cases) < int(config["minimum_beta_cases"]):
            raise ValueError("Số beta cases thấp hơn minimum_beta_cases.")
        validate_beta_cases(
            beta_cases,
            require_human_review=bool(config["require_human_review"]),
        )

    synthetic_cases = source_metadata["synthetic_cases"] if config["include_synthetic"] else 0
    benchmark_cases = source_metadata["benchmark_cases"] if config["include_benchmark"] else 0
    beta_case_count = len(beta_cases) if config["include_beta"] else 0
    total_cases = synthetic_cases + benchmark_cases + beta_case_count
    target_metadata = {
        "dataset_id": source_metadata["dataset_id"],
        "version": target_version,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source": source_metadata["source"],
        "total_cases": total_cases,
        "synthetic_cases": synthetic_cases,
        "benchmark_cases": benchmark_cases,
        "beta_cases": beta_case_count,
        "status": "draft",
        "production_safe": False,
        "promoted_from": source_version,
        "promotion_config": {
            "include_synthetic": config["include_synthetic"],
            "include_benchmark": config["include_benchmark"],
            "include_beta": config["include_beta"],
            "beta_source_path": beta_source_path,
            "require_human_review": config["require_human_review"],
        },
        "notes": str(config.get("notes") or ""),
    }
    parse_dataset_metadata_dict(target_metadata)
    return {
        "source_path": str(source_path),
        "target_path": str(target_path),
        "source_metadata": source_metadata,
        "target_metadata": target_metadata,
        "beta_case_count": beta_case_count,
    }


def load_beta_cases(path: str | Path) -> list[dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if isinstance(payload, list):
        cases = payload
    elif isinstance(payload, dict):
        cases = payload.get("cases", [])
    else:
        raise ValueError("Beta source phải là JSON array hoặc object có field cases.")
    if not isinstance(cases, list):
        raise ValueError("Beta source field cases phải là list.")
    return [dict(case) for case in cases if isinstance(case, dict)]


def validate_beta_cases(cases: list[dict[str, Any]], *, require_human_review: bool) -> None:
    for index, case in enumerate(cases, start=1):
        serialized = json.dumps(case, ensure_ascii=False)
        if MOJIBAKE_PATTERN.search(serialized):
            raise ValueError(f"Beta case #{index} có dấu hiệu mojibake.")
        pii_scan_text = ISO_TIMESTAMP_PATTERN.sub("", serialized)
        if EMAIL_PATTERN.search(serialized) or PHONE_PATTERN.search(pii_scan_text):
            raise ValueError(f"Beta case #{index} có dấu hiệu PII.")
        if require_human_review:
            review = case.get("human_review") or case.get("review_metadata")
            if not isinstance(review, dict) or review.get("reviewed") is not True:
                raise ValueError(f"Beta case #{index} thiếu human review metadata.")


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


def _require_bool(payload: dict[str, Any], field: str) -> None:
    if not isinstance(payload[field], bool):
        raise ValueError(f"{field} phải là boolean.")


def _resolve_path(root_dir: Path, path: str) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return root_dir / candidate
