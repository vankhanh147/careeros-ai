"""Training utilities for the CareerOS trainable matching prototype."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from app.ml.features import build_feature_corpus


MODEL_VERSION = "matching_model_v1"
MODEL_FILE = "matching_model.joblib"
VECTORIZER_FILE = "matching_vectorizer.joblib"
LABEL_MAPPING_FILE = "label_mapping.json"
METADATA_FILE = "model_metadata.json"


def train_matching_classifier(cases: Sequence[Mapping[str, Any]]) -> tuple[LogisticRegression, TfidfVectorizer, list[str]]:
    labels = [str(case["fit_label"]) for case in cases]
    corpus = build_feature_corpus(cases)
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=5000, min_df=1)
    features = vectorizer.fit_transform(corpus)
    model = LogisticRegression(max_iter=1000, random_state=42, class_weight="balanced")
    model.fit(features, labels)
    return model, vectorizer, sorted(set(labels))


def save_matching_artifacts(
    *,
    model: LogisticRegression,
    vectorizer: TfidfVectorizer,
    labels: Sequence[str],
    model_dir: Path,
    metadata: Mapping[str, Any],
) -> None:
    import json

    model_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_dir / MODEL_FILE)
    joblib.dump(vectorizer, model_dir / VECTORIZER_FILE)
    (model_dir / LABEL_MAPPING_FILE).write_text(
        json.dumps({"labels": list(labels), "model_version": MODEL_VERSION}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (model_dir / METADATA_FILE).write_text(
        json.dumps(dict(metadata), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

