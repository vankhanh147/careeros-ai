"""Evaluation helpers for the CareerOS matching model prototype."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

from app.ml.features import build_feature_corpus


def evaluate_matching_classifier(model: Any, vectorizer: Any, test_cases: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    true_labels = [str(case["fit_label"]) for case in test_cases]
    features = vectorizer.transform(build_feature_corpus(test_cases))
    predicted_labels = model.predict(features)
    labels = sorted(set(true_labels).union(str(label) for label in predicted_labels))
    return {
        "accuracy": float(accuracy_score(true_labels, predicted_labels)),
        "classification_report": classification_report(true_labels, predicted_labels, labels=labels, zero_division=0),
        "confusion_matrix": confusion_matrix(true_labels, predicted_labels, labels=labels).tolist(),
        "labels": labels,
    }


def format_evaluation_markdown(*, metrics: Mapping[str, Any], metadata: Mapping[str, Any]) -> str:
    labels = [str(label) for label in metrics["labels"]]
    matrix = metrics["confusion_matrix"]
    matrix_rows = "\n".join(
        f"| {label} | " + " | ".join(str(value) for value in row) + " |"
        for label, row in zip(labels, matrix)
    )
    header = "| Actual \\ Predicted | " + " | ".join(labels) + " |"
    separator = "|---" + "|---" * len(labels) + "|"
    return f"""# Phase 9.0 Model Evaluation

Date: {metadata.get("trained_at", "unknown")}

## Mục tiêu

Đánh giá baseline TF-IDF + Logistic Regression trên Synthetic Dataset V2. Kết quả này chỉ dùng cho evaluation/prototype, chưa thay thế `match_score` production.

## Dataset

- Nguồn dữ liệu: `{metadata.get("dataset_path")}`
- Tổng số case: {metadata.get("case_count")}
- Train size: {metadata.get("train_size")}
- Test size: {metadata.get("test_size")}
- Random state: {metadata.get("random_state")}

## Metrics

- Accuracy: {metrics["accuracy"]:.3f}

## Classification Report

```text
{metrics["classification_report"]}
```

## Confusion Matrix

{header}
{separator}
{matrix_rows}

## Ghi chú

- Dataset là synthetic, không phải dữ liệu beta thật.
- Model chưa được dùng làm điểm chính.
- Cần kiểm chứng thêm bằng benchmark U01-U10 và nhãn người thật trước khi cân nhắc production.
"""

