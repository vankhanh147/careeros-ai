from scripts.generate_synthetic_dataset import generate_cases
from scripts.validate_synthetic_dataset import validate_dataset


def test_validate_synthetic_dataset_generated_payload_passes():
    payload = {
        "schema_version": "careeros-synthetic-dataset-v1",
        "dataset_type": "synthetic",
        "case_count": 70,
        "cases": generate_cases(),
    }

    result = validate_dataset(payload)

    assert result["errors"] == []
    assert result["summary"]["case_count"] == 70
    assert result["summary"]["group_counts"]["exact_fit"] == 10
    assert result["summary"]["label_counts"]["mismatch"] == 20


def test_validate_synthetic_dataset_catches_pii_and_duplicate_ids():
    cases = generate_cases()
    cases[1]["case_id"] = cases[0]["case_id"]
    cases[0]["resume_summary"] = "Contact: user@example.com, phone 0901234567."
    payload = {
        "schema_version": "careeros-synthetic-dataset-v1",
        "dataset_type": "synthetic",
        "case_count": 70,
        "cases": cases,
    }

    result = validate_dataset(payload)

    assert any("case_id bị trùng" in error for error in result["errors"])
    assert any("email/PII" in error for error in result["errors"])
    assert any("số điện thoại/PII" in error for error in result["errors"])
