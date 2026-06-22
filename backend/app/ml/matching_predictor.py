"""Runtime predictor for the trainable matching prototype.

The predictor is evaluation-only. Missing artifacts, missing sklearn/joblib or
runtime errors must never break Resume/JD analysis.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from app.ml.features import build_matching_feature_text


MODEL_DIR = Path(__file__).resolve().parents[2] / "models"
MODEL_VERSION = "matching_model_v1"
MODEL_FILE = "matching_model.joblib"
VECTORIZER_FILE = "matching_vectorizer.joblib"
METADATA_FILE = "model_metadata.json"
MODEL_NOTE = "ML prediction chỉ dùng để đánh giá nội bộ, chưa thay thế điểm chính."

_MODEL_CACHE: dict[str, Any] | None = None
_LOAD_ERROR: str | None = None


def build_disabled_ml_evaluation(reason: str) -> dict[str, Any]:
    return {
        "enabled": False,
        "predicted_label": None,
        "confidence": None,
        "label_probabilities": {},
        "model_version": None,
        "production_safe": False,
        "note": MODEL_NOTE,
        "reason": reason,
    }


def predict_matching_fit(payload: Mapping[str, Any]) -> dict[str, Any]:
    artifacts = _load_artifacts()
    if artifacts is None:
        return build_disabled_ml_evaluation(_LOAD_ERROR or "model artifact is not available")

    try:
        model = artifacts["model"]
        vectorizer = artifacts["vectorizer"]
        metadata = artifacts.get("metadata", {})
        features = vectorizer.transform([build_matching_feature_text(payload)])
        probabilities = model.predict_proba(features)[0]
        classes = [str(label) for label in model.classes_]
        probability_map = {
            label: round(float(probability), 4)
            for label, probability in sorted(zip(classes, probabilities), key=lambda item: item[0])
        }
        predicted_label = str(model.predict(features)[0])
        confidence = round(float(max(probabilities)), 4)
        return {
            "enabled": True,
            "predicted_label": predicted_label,
            "confidence": confidence,
            "label_probabilities": probability_map,
            "model_version": str(metadata.get("model_version") or MODEL_VERSION),
            "production_safe": False,
            "note": MODEL_NOTE,
            "reason": None,
        }
    except Exception as exc:  # pragma: no cover - defensive runtime fallback
        return build_disabled_ml_evaluation(f"model prediction failed: {exc.__class__.__name__}")


def _load_artifacts() -> dict[str, Any] | None:
    global _MODEL_CACHE, _LOAD_ERROR
    if _MODEL_CACHE is not None:
        return _MODEL_CACHE

    model_path = MODEL_DIR / MODEL_FILE
    vectorizer_path = MODEL_DIR / VECTORIZER_FILE
    metadata_path = MODEL_DIR / METADATA_FILE
    if not model_path.exists() or not vectorizer_path.exists():
        _LOAD_ERROR = "model artifact is not available"
        return None

    try:
        import json
        import joblib

        metadata = {}
        if metadata_path.exists():
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        _MODEL_CACHE = {
            "model": joblib.load(model_path),
            "vectorizer": joblib.load(vectorizer_path),
            "metadata": metadata,
        }
        _LOAD_ERROR = None
        return _MODEL_CACHE
    except Exception as exc:  # pragma: no cover - defensive runtime fallback
        _LOAD_ERROR = f"model artifact load failed: {exc.__class__.__name__}"
        _MODEL_CACHE = None
        return None


def reset_predictor_cache() -> None:
    global _MODEL_CACHE, _LOAD_ERROR
    _MODEL_CACHE = None
    _LOAD_ERROR = None
