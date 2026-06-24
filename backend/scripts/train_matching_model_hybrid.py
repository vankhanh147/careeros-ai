"""Train Phase 9.2 hybrid feature matching model.

This script trains a separate offline artifact. It does not overwrite Phase 9.0
text-only artifacts and does not change production scoring.
"""

from __future__ import annotations

from collections import Counter
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
from scipy.sparse import hstack
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score


ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.ml.features import build_feature_corpus
from app.ml.train_matching_model import RANDOM_STATE, split_matching_cases


SYNTHETIC_DATASET_PATH = ROOT_DIR / "docs" / "datasets" / "synthetic" / "synthetic_cases.json"
HYBRID_DATASET_PATH = ROOT_DIR / "docs" / "datasets" / "synthetic" / "hybrid_training_dataset.json"
MODEL_DIR = BACKEND_DIR / "models"
TEXT_MODEL_PATH = MODEL_DIR / "matching_model.joblib"
TEXT_VECTORIZER_PATH = MODEL_DIR / "matching_vectorizer.joblib"
HYBRID_MODEL_PATH = MODEL_DIR / "hybrid_matching_model.joblib"
HYBRID_VECTORIZER_PATH = MODEL_DIR / "hybrid_matching_vectorizer.joblib"
HYBRID_METADATA_PATH = MODEL_DIR / "hybrid_model_metadata.json"
EVAL_REPORT_PATH = ROOT_DIR / "context" / "PHASE_9_2_HYBRID_FEATURE_EVAL.md"
MODEL_VERSION = "hybrid_matching_model_v1"


def load_synthetic_cases() -> list[dict[str, Any]]:
    payload = json.loads(SYNTHETIC_DATASET_PATH.read_text(encoding="utf-8"))
    return [dict(case) for case in payload.get("cases", [])]


def load_hybrid_rows() -> list[dict[str, Any]]:
    payload = json.loads(HYBRID_DATASET_PATH.read_text(encoding="utf-8"))
    return [dict(row) for row in payload.get("rows", [])]


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    synthetic_cases = load_synthetic_cases()
    train_cases, test_cases = split_matching_cases(synthetic_cases)
    hybrid_rows_by_id = {row["case_id"]: row for row in load_hybrid_rows()}
    train_rows = [hybrid_rows_by_id[case["case_id"]] for case in train_cases]
    test_rows = [hybrid_rows_by_id[case["case_id"]] for case in test_cases]

    hybrid_model, text_vectorizer, structured_vectorizer = train_hybrid_model(train_rows)
    hybrid_metrics = evaluate_hybrid_model(hybrid_model, text_vectorizer, structured_vectorizer, test_rows)
    text_metrics = evaluate_text_only_v1(test_cases)

    metadata = {
        "model_version": MODEL_VERSION,
        "model_type": "RandomForestClassifier",
        "feature_mode": "tfidf_text_plus_structured_features",
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "source_dataset": str(HYBRID_DATASET_PATH.relative_to(ROOT_DIR)),
        "case_count": len(hybrid_rows_by_id),
        "train_size": len(train_rows),
        "test_size": len(test_rows),
        "random_state": RANDOM_STATE,
        "production_safe": False,
        "note": "Hybrid model chỉ dùng cho offline evaluation, chưa thay thế điểm production.",
        "hybrid_metrics": summarize_metrics(hybrid_metrics),
        "text_only_v1_metrics": summarize_metrics(text_metrics),
    }
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump({"classifier": hybrid_model, "structured_vectorizer": structured_vectorizer}, HYBRID_MODEL_PATH)
    joblib.dump(text_vectorizer, HYBRID_VECTORIZER_PATH)
    HYBRID_METADATA_PATH.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    EVAL_REPORT_PATH.write_text(build_eval_report(text_metrics, hybrid_metrics, metadata), encoding="utf-8")

    print(f"Hybrid model version: {MODEL_VERSION}")
    print(f"Rows: {len(hybrid_rows_by_id)} | train: {len(train_rows)} | test: {len(test_rows)}")
    print(f"Text-only V1 accuracy: {text_metrics['accuracy']:.3f} | macro F1: {text_metrics['macro_f1']:.3f}")
    print(f"Hybrid accuracy: {hybrid_metrics['accuracy']:.3f} | macro F1: {hybrid_metrics['macro_f1']:.3f}")
    print(f"Artifacts: {HYBRID_MODEL_PATH}, {HYBRID_VECTORIZER_PATH}")
    print(f"Eval report: {EVAL_REPORT_PATH}")
    return 0


def train_hybrid_model(rows: list[dict[str, Any]]) -> tuple[RandomForestClassifier, TfidfVectorizer, DictVectorizer]:
    labels = [str(row["label"]) for row in rows]
    text_vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=5000, min_df=1)
    structured_vectorizer = DictVectorizer(sparse=True)
    text_features = text_vectorizer.fit_transform([str(row["text_input"]) for row in rows])
    structured_features = structured_vectorizer.fit_transform([dict(row["structured_features"]) for row in rows])
    features = hstack([text_features, structured_features])
    model = RandomForestClassifier(n_estimators=200, random_state=RANDOM_STATE, class_weight="balanced", n_jobs=1)
    model.fit(features, labels)
    return model, text_vectorizer, structured_vectorizer


def evaluate_hybrid_model(
    model: RandomForestClassifier,
    text_vectorizer: TfidfVectorizer,
    structured_vectorizer: DictVectorizer,
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    labels = [str(row["label"]) for row in rows]
    text_features = text_vectorizer.transform([str(row["text_input"]) for row in rows])
    structured_features = structured_vectorizer.transform([dict(row["structured_features"]) for row in rows])
    predictions = model.predict(hstack([text_features, structured_features]))
    return build_metrics(labels, [str(prediction) for prediction in predictions], rows)


def evaluate_text_only_v1(test_cases: list[dict[str, Any]]) -> dict[str, Any]:
    model = joblib.load(TEXT_MODEL_PATH)
    vectorizer = joblib.load(TEXT_VECTORIZER_PATH)
    labels = [str(case["fit_label"]) for case in test_cases]
    predictions = model.predict(vectorizer.transform(build_feature_corpus(test_cases)))
    rows = [{"source_category": str(case.get("category") or case.get("group") or "")} for case in test_cases]
    return build_metrics(labels, [str(prediction) for prediction in predictions], rows)


def build_metrics(labels: list[str], predictions: list[str], rows: list[dict[str, Any]]) -> dict[str, Any]:
    all_labels = sorted(set(labels).union(predictions))
    category_errors: Counter[str] = Counter()
    category_totals: Counter[str] = Counter()
    for label, prediction, row in zip(labels, predictions, rows):
        category = str(row.get("source_category") or "unknown")
        category_totals[category] += 1
        if label != prediction:
            category_errors[category] += 1
    return {
        "accuracy": float(accuracy_score(labels, predictions)),
        "macro_f1": float(f1_score(labels, predictions, average="macro", zero_division=0)),
        "labels": all_labels,
        "classification_report": classification_report(labels, predictions, labels=all_labels, zero_division=0),
        "confusion_matrix": confusion_matrix(labels, predictions, labels=all_labels).tolist(),
        "error_counts": dict(Counter(f"{label}->{prediction}" for label, prediction in zip(labels, predictions))),
        "good_to_medium": sum(1 for label, prediction in zip(labels, predictions) if label == "good" and prediction == "medium"),
        "mismatch_to_medium": sum(1 for label, prediction in zip(labels, predictions) if label == "mismatch" and prediction == "medium"),
        "weak_errors": sum(1 for label, prediction in zip(labels, predictions) if label == "weak" and prediction != "weak"),
        "category_errors": {
            category: {
                "errors": category_errors[category],
                "total": category_totals[category],
                "error_rate": round(category_errors[category] / category_totals[category], 3) if category_totals[category] else 0,
            }
            for category in sorted(category_totals)
        },
    }


def summarize_metrics(metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        "accuracy": metrics["accuracy"],
        "macro_f1": metrics["macro_f1"],
        "good_to_medium": metrics["good_to_medium"],
        "mismatch_to_medium": metrics["mismatch_to_medium"],
        "weak_errors": metrics["weak_errors"],
    }


def build_eval_report(text_metrics: dict[str, Any], hybrid_metrics: dict[str, Any], metadata: dict[str, Any]) -> str:
    labels = hybrid_metrics["labels"]
    text_matrix = matrix_markdown(text_metrics, labels)
    hybrid_matrix = matrix_markdown(hybrid_metrics, labels)
    category_rows = "\n".join(
        f"| {category} | {value['errors']} | {value['total']} | {value['error_rate']} |"
        for category, value in hybrid_metrics["category_errors"].items()
    )
    return f"""# Phase 9.2 - Hybrid Feature Evaluation

Date: {metadata['trained_at']}

## Mục tiêu

So sánh model text-only V1 với model hybrid dùng TF-IDF text features và structured features từ rule-based matcher, taxonomy, semantic/hybrid metadata và dataset metadata. Phase này chỉ là offline evaluation, không thay production scoring.

## So sánh metrics

| Model | Accuracy | Macro F1 | good -> medium | mismatch -> medium | weak errors |
| --- | ---: | ---: | ---: | ---: | ---: |
| Text-only V1 | {text_metrics['accuracy']:.3f} | {text_metrics['macro_f1']:.3f} | {text_metrics['good_to_medium']} | {text_metrics['mismatch_to_medium']} | {text_metrics['weak_errors']} |
| Hybrid feature model | {hybrid_metrics['accuracy']:.3f} | {hybrid_metrics['macro_f1']:.3f} | {hybrid_metrics['good_to_medium']} | {hybrid_metrics['mismatch_to_medium']} | {hybrid_metrics['weak_errors']} |

## Confusion matrix của Text-only V1

{text_matrix}

## Confusion matrix của Hybrid model

{hybrid_matrix}

## Tổng hợp lỗi theo category của Hybrid model

| Category | Errors | Total | Error rate |
| --- | ---: | ---: | ---: |
{category_rows}

## Nhận xét

- Hybrid model dùng thêm tín hiệu từ matcher nên kỳ vọng giảm lỗi boundary `good -> medium` và `mismatch -> medium`.
- Nếu metrics cải thiện nhưng phụ thuộc quá nhiều vào `rule_based_score`, model vẫn chỉ nên được xem là evaluator phụ, không phải replacement cho matcher.
- Semantic đang disabled trong môi trường hiện tại nên `semantic_available=0` và `semantic_similarity=0` cho dataset được build ở phase này.

## Kết luận

Hybrid feature model là bước tốt hơn text-only để học từ tri thức rule-based hiện có. Tuy nhiên, dữ liệu vẫn là synthetic nên chưa đủ cơ sở để đưa vào production scoring.
"""


def matrix_markdown(metrics: dict[str, Any], labels: list[str]) -> str:
    header = "| Actual \\ Predicted | " + " | ".join(labels) + " |"
    separator = "|---" + "|---" * len(labels) + "|"
    rows = "\n".join(
        f"| {label} | " + " | ".join(str(value) for value in row) + " |"
        for label, row in zip(labels, metrics["confusion_matrix"])
    )
    return f"{header}\n{separator}\n{rows}"


if __name__ == "__main__":
    raise SystemExit(main())
