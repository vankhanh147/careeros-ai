import json
from pathlib import Path

from scripts.build_training_dataset import (
    build_statistics,
    build_training_dataset,
    export_training_dataset,
    run_assembly,
    sha256_text,
    stable_json,
    validate_training_cases,
)


def tiny_case(case_id="CASE001", **overrides):
    case = {
        "case_id": case_id,
        "source": "synthetic",
        "source_category": "exact_fit",
        "seniority": "Intern",
        "candidate_profile": "Ứng viên backend synthetic.",
        "resume_summary": "CV synthetic có REST API và JWT.",
        "job_description_summary": "JD synthetic yêu cầu REST API và JWT.",
        "target_role": "Backend Developer",
        "role_family": "backend",
        "candidate_stack": "Python",
        "jd_stack": "FastAPI",
        "fit_label": "good",
        "expected_score_range": "75-90",
        "reason": "Case synthetic hợp lệ cho kiểm tra assembly.",
        "skill_overlap": ["REST API", "JWT"],
        "missing_critical_skills": [],
        "review_status": "not_required",
        "approved_for_training": True,
        "anonymized": True,
        "content_hash": "hash-" + case_id,
    }
    case.update(overrides)
    return case


def test_duplicate_case_id_detection():
    result = validate_training_cases([tiny_case("DUP001"), tiny_case("DUP001", content_hash="hash-DUP002")])

    assert any("case_id bị trùng" in error for error in result["errors"])


def test_duplicate_content_hash_detection():
    result = validate_training_cases([tiny_case("CASE001", content_hash="same"), tiny_case("CASE002", content_hash="same")])

    assert any("content hash bị trùng" in error for error in result["errors"])


def test_validation_failure_for_missing_label():
    result = validate_training_cases([tiny_case("CASE001", fit_label="")])

    assert any("thiếu label" in error for error in result["errors"])


def test_validation_failure_for_unapproved_beta():
    result = validate_training_cases([
        tiny_case(
            "BETA001",
            source="beta",
            review_status="UNDER_REVIEW",
            approved_for_training=False,
            anonymized=True,
        )
    ])

    assert any("beta review chưa approved" in error for error in result["errors"])


def test_export_artifact_manifest_statistics_and_fingerprint(tmp_path):
    payload = {
        "schema_version": "careeros-training-dataset-v1",
        "dataset_version": "dataset_test",
        "created_at": "2026-06-26T00:00:00Z",
        "case_count": 2,
        "sources": {"synthetic": 1, "benchmark": 1, "beta": 0},
        "cases": [tiny_case("CASE001"), tiny_case("CASE002", source="benchmark", source_category="role_mismatch")],
    }
    artifact = tmp_path / "training_dataset.json"
    manifest = tmp_path / "manifest.json"
    stats = tmp_path / "statistics.json"

    result = export_training_dataset(
        payload=payload,
        artifact_path=artifact,
        manifest_path=manifest,
        statistics_path=stats,
        source_files={"synthetic": "synthetic.json", "benchmark": "benchmark.md", "beta_reviews": ""},
    )

    assert artifact.exists()
    assert manifest.exists()
    assert stats.exists()
    manifest_payload = json.loads(manifest.read_text(encoding="utf-8"))
    assert manifest_payload["artifact_hash"] == sha256_text(stable_json(payload))
    assert manifest_payload["total_cases"] == 2
    stats_payload = json.loads(stats.read_text(encoding="utf-8"))
    assert stats_payload["source_distribution"] == {"benchmark": 1, "synthetic": 1}
    assert result["statistics"]["label_distribution"]["good"] == 2


def test_build_statistics_distribution():
    payload = {
        "dataset_version": "dataset_test",
        "cases": [
            tiny_case("CASE001", source="synthetic", role_family="backend", fit_label="good"),
            tiny_case("CASE002", source="beta", role_family="frontend", fit_label="weak", approved_for_training=True),
        ],
    }

    stats = build_statistics(payload)

    assert stats["source_distribution"] == {"beta": 1, "synthetic": 1}
    assert stats["approved_beta_percent"] == 100.0
    assert stats["label_distribution"] == {"good": 1, "weak": 1}


def test_run_assembly_dry_run_does_not_write(tmp_path):
    artifact = tmp_path / "artifact.json"
    manifest = tmp_path / "manifest.json"
    stats = tmp_path / "stats.json"

    result = run_assembly(
        dataset_version="dataset_test",
        beta_reviews_path=None,
        dry_run=True,
        artifact_path=artifact,
        manifest_path=manifest,
        statistics_path=stats,
    )

    assert result["ok"] is True
    assert result["dry_run"] is True
    assert not artifact.exists()
    assert not manifest.exists()
    assert not stats.exists()
    assert result["payload"]["case_count"] == 310


def test_build_training_dataset_default_sources():
    result = build_training_dataset(dataset_version="dataset_test")

    assert result["validation"]["errors"] == []
    assert result["payload"]["sources"] == {"synthetic": 300, "benchmark": 10, "beta": 0}
    assert result["payload"]["case_count"] == 310