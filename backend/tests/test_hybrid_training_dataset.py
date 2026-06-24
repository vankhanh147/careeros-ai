import json
from pathlib import Path

from app.ml.features import HYBRID_STRUCTURED_FEATURE_KEYS, build_hybrid_structured_features
from app.services.resume_job_matcher import analyze_resume_job_match
from scripts.build_hybrid_training_dataset import build_hybrid_rows
from scripts.train_matching_model_hybrid import (
    HYBRID_MODEL_PATH,
    HYBRID_VECTORIZER_PATH,
    TEXT_MODEL_PATH,
    TEXT_VECTORIZER_PATH,
    train_hybrid_model,
)
from scripts.validate_hybrid_training_dataset import validate_hybrid_dataset


ROOT_DIR = Path(__file__).resolve().parents[2]
HYBRID_DATASET_PATH = ROOT_DIR / "docs" / "datasets" / "synthetic" / "hybrid_training_dataset.json"
SYNTHETIC_DATASET_PATH = ROOT_DIR / "docs" / "datasets" / "synthetic" / "synthetic_cases.json"


def test_hybrid_feature_extraction_has_required_keys():
    case = {
        "case_id": "T001",
        "resume_summary": "CV có project Backend dùng Python FastAPI REST API PostgreSQL JWT.",
        "job_description_summary": "JD yêu cầu Backend Python FastAPI REST API PostgreSQL JWT Docker.",
        "target_role": "Backend Developer",
        "role_family": "backend",
        "candidate_stack": "Python, FastAPI",
        "jd_stack": "Python, FastAPI, Docker",
        "seniority": "Intern",
        "category": "exact_fit",
        "fit_label": "good",
        "expected_score_range": "75-90",
        "missing_critical_skills": ["Docker"],
        "skill_overlap": ["Python", "FastAPI", "REST API", "PostgreSQL", "JWT"],
    }
    analysis = analyze_resume_job_match(case["resume_summary"], case["job_description_summary"])

    features = build_hybrid_structured_features(case, analysis)

    assert set(HYBRID_STRUCTURED_FEATURE_KEYS).issubset(features)
    assert features["rule_based_score"] == analysis["match_score"]
    assert features["matched_skill_count"] > 0
    assert features["semantic_available"] in {0, 1}


def test_hybrid_dataset_builder_creates_rows_for_sample_cases():
    cases = json.loads(SYNTHETIC_DATASET_PATH.read_text(encoding="utf-8"))["cases"][:3]

    rows = build_hybrid_rows(cases)

    assert len(rows) == 3
    assert all("text_input" in row for row in rows)
    assert all("structured_features" in row for row in rows)
    assert all("label" in row for row in rows)


def test_generated_hybrid_dataset_validator_passes():
    payload = json.loads(HYBRID_DATASET_PATH.read_text(encoding="utf-8"))

    result = validate_hybrid_dataset(payload)

    assert result["errors"] == []
    assert result["summary"]["row_count"] == 300


def test_hybrid_training_sample_does_not_use_v1_artifact_names():
    payload = json.loads(HYBRID_DATASET_PATH.read_text(encoding="utf-8"))
    rows = payload["rows"][:12]

    model, text_vectorizer, structured_vectorizer = train_hybrid_model(rows)

    assert model is not None
    assert text_vectorizer is not None
    assert structured_vectorizer is not None
    assert HYBRID_MODEL_PATH.name != TEXT_MODEL_PATH.name
    assert HYBRID_VECTORIZER_PATH.name != TEXT_VECTORIZER_PATH.name

