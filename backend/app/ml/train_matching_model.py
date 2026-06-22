"""Shared training pipeline for the matching model prototype."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from sklearn.model_selection import train_test_split

from app.ml.evaluate_model import evaluate_matching_classifier
from app.ml.matching_model import train_matching_classifier


RANDOM_STATE = 42
TEST_SIZE = 0.25


def split_matching_cases(
    cases: Sequence[Mapping[str, Any]],
    *,
    test_size: float = TEST_SIZE,
    random_state: int = RANDOM_STATE,
) -> tuple[list[Mapping[str, Any]], list[Mapping[str, Any]]]:
    labels = [str(case["fit_label"]) for case in cases]
    train_cases, test_cases = train_test_split(
        list(cases),
        test_size=test_size,
        random_state=random_state,
        stratify=labels,
    )
    return train_cases, test_cases


def train_and_evaluate_matching_model(
    cases: Sequence[Mapping[str, Any]],
    *,
    test_size: float = TEST_SIZE,
    random_state: int = RANDOM_STATE,
) -> dict[str, Any]:
    train_cases, test_cases = split_matching_cases(cases, test_size=test_size, random_state=random_state)
    model, vectorizer, labels = train_matching_classifier(train_cases)
    metrics = evaluate_matching_classifier(model, vectorizer, test_cases)
    return {
        "model": model,
        "vectorizer": vectorizer,
        "labels": labels,
        "metrics": metrics,
        "train_cases": train_cases,
        "test_cases": test_cases,
    }

