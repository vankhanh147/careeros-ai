from pathlib import Path

from app.ml.features import build_matching_feature_text
from app.ml.matching_model import MODEL_VERSION, save_matching_artifacts, train_matching_classifier
from app.ml import matching_predictor


SAMPLE_CASE = {
    "case_id": "TEST001",
    "resume_summary": "CV có project Backend dùng Python, FastAPI, REST API và PostgreSQL.",
    "job_description_summary": "JD yêu cầu Backend Developer biết Python, FastAPI, REST API, JWT và PostgreSQL.",
    "target_role": "Backend Developer",
    "role_family": "backend",
    "candidate_stack": "Python, FastAPI, PostgreSQL",
    "jd_stack": "Python, FastAPI, PostgreSQL, JWT",
    "fit_label": "good",
    "missing_critical_skills": ["JWT"],
    "skill_overlap": ["Python", "FastAPI", "REST API", "PostgreSQL"],
}


def test_matching_feature_extraction_from_synthetic_case():
    feature_text = build_matching_feature_text(SAMPLE_CASE)

    assert "resume_summary:" in feature_text
    assert "job_description_summary:" in feature_text
    assert "Backend Developer" in feature_text
    assert "JWT" in feature_text
    assert "fit_label" not in feature_text


def test_predictor_fallback_when_artifacts_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(matching_predictor, "MODEL_DIR", tmp_path)
    matching_predictor.reset_predictor_cache()

    result = matching_predictor.predict_matching_fit(SAMPLE_CASE)

    assert result["enabled"] is False
    assert result["predicted_label"] is None
    assert result["label_probabilities"] == {}
    assert "artifact" in result["reason"]


def test_predictor_loads_mock_artifact(monkeypatch, tmp_path: Path):
    cases = [
        SAMPLE_CASE,
        {
            **SAMPLE_CASE,
            "case_id": "TEST002",
            "resume_summary": "CV Frontend React TypeScript nhưng JD backend .NET.",
            "job_description_summary": "JD yêu cầu ASP.NET Core, C#, SQL và JWT.",
            "role_family": "backend",
            "candidate_stack": "React, TypeScript",
            "jd_stack": "ASP.NET Core, C#, SQL",
            "fit_label": "mismatch",
            "missing_critical_skills": ["ASP.NET Core", "C#"],
            "skill_overlap": [],
        },
        {
            **SAMPLE_CASE,
            "case_id": "TEST003",
            "resume_summary": "CV backend Node.js Express JWT MongoDB.",
            "job_description_summary": "JD backend .NET cần ASP.NET Core, C#, SQL, JWT.",
            "candidate_stack": "Node.js, Express, MongoDB",
            "jd_stack": "ASP.NET Core, C#, SQL",
            "fit_label": "medium",
            "missing_critical_skills": ["ASP.NET Core", "C#"],
            "skill_overlap": ["JWT"],
        },
        {
            **SAMPLE_CASE,
            "case_id": "TEST004",
            "resume_summary": "CV rất ngắn chỉ liệt kê Python và SQL, thiếu project.",
            "job_description_summary": "JD cần Backend Developer với API, database, JWT và evidence project.",
            "candidate_stack": "Python, SQL",
            "jd_stack": "Python, REST API, PostgreSQL, JWT",
            "fit_label": "weak",
            "missing_critical_skills": ["REST API", "JWT"],
            "skill_overlap": ["Python", "SQL"],
        },
    ]
    model, vectorizer, labels = train_matching_classifier(cases)
    save_matching_artifacts(
        model=model,
        vectorizer=vectorizer,
        labels=labels,
        model_dir=tmp_path,
        metadata={"model_version": MODEL_VERSION},
    )
    monkeypatch.setattr(matching_predictor, "MODEL_DIR", tmp_path)
    matching_predictor.reset_predictor_cache()

    result = matching_predictor.predict_matching_fit(SAMPLE_CASE)

    assert result["enabled"] is True
    assert result["predicted_label"] in {"good", "medium", "weak", "mismatch"}
    assert result["model_version"] == MODEL_VERSION
    assert result["production_safe"] is False
    assert result["confidence"] is not None
    assert set(result["label_probabilities"]).issuperset({"good", "medium", "weak", "mismatch"})

