from scripts.generate_synthetic_dataset import generate_cases
from scripts.validate_synthetic_dataset import EXPECTED_CATEGORIES, EXPECTED_ROLES, EXPECTED_SENIORITIES, validate_dataset


def _payload_from_generated_cases():
    cases = generate_cases()
    return {
        "schema_version": "careeros-synthetic-dataset-v2",
        "dataset_type": "synthetic",
        "case_count": len(cases),
        "cases": cases,
    }


def test_validate_synthetic_dataset_generated_payload_passes():
    result = validate_dataset(_payload_from_generated_cases())

    assert result["errors"] == []
    assert result["summary"]["case_count"] == 300
    assert set(result["summary"]["category_counts"]) == EXPECTED_CATEGORIES
    assert all(count == 30 for count in result["summary"]["category_counts"].values())
    assert set(result["summary"]["role_counts"]) == EXPECTED_ROLES
    assert set(result["summary"]["seniority_counts"]) == EXPECTED_SENIORITIES


def test_validate_synthetic_dataset_catches_pii_and_duplicate_ids():
    payload = _payload_from_generated_cases()
    cases = payload["cases"]
    cases[1]["case_id"] = cases[0]["case_id"]
    cases[0]["resume_summary"] = "Contact: user@example.com, phone 0901234567."

    result = validate_dataset(payload)

    assert any("case_id bị trùng" in error for error in result["errors"])
    assert any("email/PII" in error for error in result["errors"])
    assert any("số điện thoại/PII" in error for error in result["errors"])


def test_validate_synthetic_dataset_catches_missing_seniority_and_role_coverage():
    payload = _payload_from_generated_cases()
    for case in payload["cases"]:
        if case["seniority"] == "Mid-level":
            case["seniority"] = "Junior"
        if case["target_role"] == "Cybersecurity Analyst":
            case["target_role"] = "Backend Developer"

    result = validate_dataset(payload)

    assert any("Thiếu role coverage" in error for error in result["errors"])
    assert any("Thiếu seniority coverage" in error for error in result["errors"])