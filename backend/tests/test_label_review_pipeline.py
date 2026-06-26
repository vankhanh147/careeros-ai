import json
import subprocess
import sys
from pathlib import Path

import pytest

from app.ml.training_infra import (
    parse_label_review_schema,
    validate_label_review_case,
    validate_label_review_cases,
    validate_label_review_file,
)


BACKEND_DIR = Path(__file__).resolve().parents[1]
SCHEMA_PATH = BACKEND_DIR / "ml" / "configs" / "label_review_schema.json"
SAMPLE_PATH = BACKEND_DIR / "ml" / "reviews" / "sample_review_cases.json"


def valid_case(**overrides):
    case = {
        "case_id": "BETA_TEST_001",
        "dataset_version": "dataset_v3_draft",
        "previous_status": "UNDER_REVIEW",
        "review_status": "APPROVED",
        "reviewer": "internal_reviewer",
        "review_time": "2026-06-26T00:00:00Z",
        "label_confidence": 0.82,
        "disagreement_reason": "Reviewer đồng ý với expected label sau khi kiểm tra evidence.",
        "notes": "Case đã ẩn danh và đủ điều kiện QA.",
        "approved_for_training": True,
        "anonymized": True,
    }
    case.update(overrides)
    return case


def test_parse_label_review_schema():
    schema = parse_label_review_schema(SCHEMA_PATH)

    assert schema["schema_id"] == "careeros_label_review_schema_v1"
    assert "APPROVED" in schema["allowed_statuses"]
    assert "case_id" in schema["required_fields"]


def test_validate_sample_review_file():
    result = validate_label_review_file(SAMPLE_PATH)

    assert result["total_cases"] == 2
    assert result["errors_count"] == 0
    assert result["ready_for_promotion_count"] == 1


def test_invalid_status_returns_error():
    errors = validate_label_review_case(valid_case(review_status="DONE"))

    assert any("review_status không hợp lệ" in error for error in errors)


def test_invalid_transition_returns_error():
    errors = validate_label_review_case(valid_case(previous_status="NEW", review_status="APPROVED"))

    assert any("Transition không hợp lệ" in error for error in errors)


def test_missing_reviewer_returns_error():
    errors = validate_label_review_case(valid_case(reviewer=""))

    assert any("reviewer bắt buộc" in error for error in errors)


def test_missing_confidence_returns_error():
    case = valid_case()
    case.pop("label_confidence")
    errors = validate_label_review_case(case)

    assert any("label_confidence" in error for error in errors)


def test_missing_anonymization_returns_error():
    errors = validate_label_review_case(valid_case(anonymized=False))

    assert any("anonymized=true" in error for error in errors)


def test_approved_for_training_before_approved_returns_error():
    errors = validate_label_review_case(
        valid_case(previous_status="ANONYMIZED", review_status="UNDER_REVIEW", approved_for_training=True)
    )

    assert any("approved_for_training chỉ được true" in error for error in errors)


def test_validate_label_review_cases_summary():
    result = validate_label_review_cases([valid_case(), valid_case(case_id="BETA_TEST_002", review_status="DONE")])

    assert result["total_cases"] == 2
    assert result["errors_count"] >= 1
    assert result["ready_for_promotion_count"] == 1


def test_label_review_script_runs():
    result = subprocess.run(
        [sys.executable, "scripts/validate_label_review_pipeline.py"],
        cwd=BACKEND_DIR,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    assert "CareerOS Label Review QA" in result.stdout
    assert "Ready for promotion" in result.stdout