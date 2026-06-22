"""Train the CareerOS AI matching model prototype from synthetic data.

Run from `backend/`:

    python scripts/train_matching_model.py

The script does not use real user data and does not change production scoring.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.ml.evaluate_model import format_evaluation_markdown
from app.ml.matching_model import MODEL_VERSION, save_matching_artifacts
from app.ml.train_matching_model import RANDOM_STATE, TEST_SIZE, train_and_evaluate_matching_model

DATASET_PATH = ROOT_DIR / "docs" / "datasets" / "synthetic" / "synthetic_cases.json"
MODEL_DIR = BACKEND_DIR / "models"
EVAL_REPORT_PATH = ROOT_DIR / "context" / "PHASE_9_0_MODEL_EVAL.md"


def load_synthetic_cases(dataset_path: Path = DATASET_PATH) -> list[dict[str, Any]]:
    payload = json.loads(dataset_path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        cases = payload
    else:
        cases = payload.get("cases", [])
    if not isinstance(cases, list) or not cases:
        raise ValueError("Synthetic dataset does not contain cases")
    return [dict(case) for case in cases]


def main() -> None:
    cases = load_synthetic_cases()
    training_result = train_and_evaluate_matching_model(cases, test_size=TEST_SIZE, random_state=RANDOM_STATE)
    model = training_result["model"]
    vectorizer = training_result["vectorizer"]
    all_labels = training_result["labels"]
    metrics = training_result["metrics"]
    train_cases = training_result["train_cases"]
    test_cases = training_result["test_cases"]
    metadata = {
        "model_version": MODEL_VERSION,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "dataset_path": str(DATASET_PATH.relative_to(ROOT_DIR)),
        "case_count": len(cases),
        "train_size": len(train_cases),
        "test_size": len(test_cases),
        "random_state": RANDOM_STATE,
        "test_size_ratio": TEST_SIZE,
        "accuracy": metrics["accuracy"],
        "labels": all_labels,
        "production_safe": False,
        "note": "Model chỉ dùng cho evaluation/prototype, chưa thay thế điểm production.",
    }

    save_matching_artifacts(
        model=model,
        vectorizer=vectorizer,
        labels=all_labels,
        model_dir=MODEL_DIR,
        metadata=metadata,
    )
    EVAL_REPORT_PATH.write_text(
        format_evaluation_markdown(metrics=metrics, metadata=metadata),
        encoding="utf-8",
    )

    print(f"Model version: {MODEL_VERSION}")
    print(f"Cases: {len(cases)} | train: {len(train_cases)} | test: {len(test_cases)}")
    print(f"Accuracy: {metrics['accuracy']:.3f}")
    print(metrics["classification_report"])
    print(f"Artifacts saved to: {MODEL_DIR}")
    print(f"Evaluation report: {EVAL_REPORT_PATH}")


if __name__ == "__main__":
    main()
