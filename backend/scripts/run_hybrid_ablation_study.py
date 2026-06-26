"""Run Phase 9.3 hybrid model ablation study.

This script trains temporary offline models for evaluation only. It does not
overwrite Phase 9.0 or Phase 9.2 model artifacts and does not change production
scoring.
"""

from __future__ import annotations

from collections import Counter
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scipy.sparse import hstack
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score


ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.ml.features import HYBRID_STRUCTURED_FEATURE_KEYS, build_hybrid_structured_features, build_matching_feature_text
from app.ml.train_matching_model import RANDOM_STATE, split_matching_cases
from app.services.resume_job_matcher import analyze_resume_job_match
from scripts.run_ml_benchmark_analysis import BENCHMARK_CASES


SYNTHETIC_DATASET_PATH = ROOT_DIR / "docs" / "datasets" / "synthetic" / "synthetic_cases.json"
HYBRID_DATASET_PATH = ROOT_DIR / "docs" / "datasets" / "synthetic" / "hybrid_training_dataset.json"
REPORT_PATH = ROOT_DIR / "context" / "PHASE_9_3_ABLATION_STUDY_REPORT.md"
DATASET_REPORT_PATH = ROOT_DIR / "docs" / "datasets" / "synthetic" / "ablation_results_v1.md"
METADATA_PATH = BACKEND_DIR / "models" / "hybrid_ablation_metadata.json"


STRUCTURED_WITHOUT_RULE_SCORE_KEYS = tuple(
    key for key in HYBRID_STRUCTURED_FEATURE_KEYS if key != "rule_based_score"
)
STRUCTURED_CORE_KEYS = (
    "role_alignment_score",
    "evidence_score",
    "missing_critical_skill_count",
    "matched_skill_count",
    "role_family_match",
    "stack_group_match_count",
)
LABEL_RANK = {"mismatch": 0, "weak": 1, "medium": 2, "good": 3}


@dataclass(frozen=True)
class AblationConfig:
    key: str
    title: str
    use_text: bool
    structured_keys: tuple[str, ...]


ABLATION_CONFIGS: tuple[AblationConfig, ...] = (
    AblationConfig(
        key="text_only",
        title="A. Text-only baseline",
        use_text=True,
        structured_keys=(),
    ),
    AblationConfig(
        key="structured_without_rule_score",
        title="B. Structured không có rule_based_score",
        use_text=False,
        structured_keys=STRUCTURED_WITHOUT_RULE_SCORE_KEYS,
    ),
    AblationConfig(
        key="structured_core_only",
        title="C. Structured core only",
        use_text=False,
        structured_keys=STRUCTURED_CORE_KEYS,
    ),
    AblationConfig(
        key="full_hybrid",
        title="D. Full hybrid",
        use_text=True,
        structured_keys=HYBRID_STRUCTURED_FEATURE_KEYS,
    ),
)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    synthetic_cases = load_synthetic_cases()
    train_cases, test_cases = split_matching_cases(synthetic_cases)
    hybrid_rows_by_id = {row["case_id"]: row for row in load_hybrid_rows()}
    train_rows = [hybrid_rows_by_id[case["case_id"]] for case in train_cases]
    test_rows = [hybrid_rows_by_id[case["case_id"]] for case in test_cases]
    benchmark_rows = build_benchmark_rows()

    ablation_results: dict[str, dict[str, Any]] = {}
    benchmark_results: dict[str, list[dict[str, Any]]] = {}
    for config in ABLATION_CONFIGS:
        model_bundle = train_config(config, train_rows)
        metrics = evaluate_config(config, model_bundle, test_rows)
        ablation_results[config.key] = {
            "title": config.title,
            "metrics": metrics,
            "top_structured_features": extract_structured_feature_importance(model_bundle, limit=20),
        }
        benchmark_results[config.key] = predict_benchmark_rows(config, model_bundle, benchmark_rows)

    metadata = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_dataset": str(HYBRID_DATASET_PATH.relative_to(ROOT_DIR)),
        "train_size": len(train_rows),
        "test_size": len(test_rows),
        "random_state": RANDOM_STATE,
        "production_safe": False,
        "configs": {
            key: {
                "title": value["title"],
                "metrics": summarize_metrics(value["metrics"]),
            }
            for key, value in ablation_results.items()
        },
    }
    METADATA_PATH.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    report = build_report(metadata, ablation_results, benchmark_results)
    REPORT_PATH.write_text(report, encoding="utf-8")
    DATASET_REPORT_PATH.write_text(build_dataset_report(metadata, ablation_results), encoding="utf-8")

    print("CareerOS Phase 9.3 Hybrid Ablation Study")
    print("=" * 48)
    for config in ABLATION_CONFIGS:
        metrics = ablation_results[config.key]["metrics"]
        print(
            f"{config.key}: accuracy={metrics['accuracy']:.3f}, "
            f"macro_f1={metrics['macro_f1']:.3f}, "
            f"good->medium={metrics['good_to_medium']}, "
            f"mismatch->medium={metrics['mismatch_to_medium']}, "
            f"weak_errors={metrics['weak_errors']}"
        )
    print(f"Report: {REPORT_PATH}")
    print(f"Dataset report: {DATASET_REPORT_PATH}")
    print(f"Metadata: {METADATA_PATH}")
    return 0


def load_synthetic_cases() -> list[dict[str, Any]]:
    payload = json.loads(SYNTHETIC_DATASET_PATH.read_text(encoding="utf-8"))
    return [dict(case) for case in payload.get("cases", [])]


def load_hybrid_rows() -> list[dict[str, Any]]:
    payload = json.loads(HYBRID_DATASET_PATH.read_text(encoding="utf-8"))
    return [dict(row) for row in payload.get("rows", [])]


def train_config(config: AblationConfig, rows: list[dict[str, Any]]) -> dict[str, Any]:
    labels = [str(row["label"]) for row in rows]
    text_vectorizer: TfidfVectorizer | None = None
    structured_vectorizer: DictVectorizer | None = None
    feature_parts = []
    text_feature_count = 0

    if config.use_text:
        text_vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=5000, min_df=1)
        text_features = text_vectorizer.fit_transform([str(row["text_input"]) for row in rows])
        text_feature_count = text_features.shape[1]
        feature_parts.append(text_features)

    if config.structured_keys:
        structured_vectorizer = DictVectorizer(sparse=True)
        structured_features = structured_vectorizer.fit_transform(
            [select_structured_features(row, config.structured_keys) for row in rows]
        )
        feature_parts.append(structured_features)

    model = RandomForestClassifier(n_estimators=200, random_state=RANDOM_STATE, class_weight="balanced", n_jobs=1)
    model.fit(_combine_feature_parts(feature_parts), labels)
    return {
        "model": model,
        "text_vectorizer": text_vectorizer,
        "structured_vectorizer": structured_vectorizer,
        "text_feature_count": text_feature_count,
        "config": config,
    }


def evaluate_config(config: AblationConfig, model_bundle: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    labels = [str(row["label"]) for row in rows]
    predictions = predict_rows(config, model_bundle, rows)
    return build_metrics(labels, [item["predicted_label"] for item in predictions], rows)


def predict_rows(config: AblationConfig, model_bundle: dict[str, Any], rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    features = transform_rows(config, model_bundle, rows)
    model: RandomForestClassifier = model_bundle["model"]
    labels = [str(label) for label in model.predict(features)]
    probabilities = model.predict_proba(features) if hasattr(model, "predict_proba") else None
    classes = [str(item) for item in getattr(model, "classes_", [])]
    predictions: list[dict[str, Any]] = []
    for index, label in enumerate(labels):
        confidence = 0.0
        label_probabilities: dict[str, float] = {}
        if probabilities is not None:
            row_probabilities = probabilities[index]
            label_probabilities = {
                class_label: round(float(probability), 4)
                for class_label, probability in zip(classes, row_probabilities)
            }
            confidence = max(label_probabilities.values()) if label_probabilities else 0.0
        predictions.append({
            "predicted_label": label,
            "confidence": round(float(confidence), 4),
            "label_probabilities": label_probabilities,
        })
    return predictions


def transform_rows(config: AblationConfig, model_bundle: dict[str, Any], rows: list[dict[str, Any]]) -> Any:
    feature_parts = []
    text_vectorizer: TfidfVectorizer | None = model_bundle["text_vectorizer"]
    structured_vectorizer: DictVectorizer | None = model_bundle["structured_vectorizer"]

    if config.use_text and text_vectorizer is not None:
        feature_parts.append(text_vectorizer.transform([str(row["text_input"]) for row in rows]))

    if config.structured_keys and structured_vectorizer is not None:
        feature_parts.append(structured_vectorizer.transform(
            [select_structured_features(row, config.structured_keys) for row in rows]
        ))

    return _combine_feature_parts(feature_parts)


def select_structured_features(row: dict[str, Any], keys: tuple[str, ...]) -> dict[str, Any]:
    structured = dict(row.get("structured_features") or {})
    return {key: structured.get(key, 0) for key in keys}


def _combine_feature_parts(feature_parts: list[Any]) -> Any:
    if len(feature_parts) == 1:
        return feature_parts[0]
    return hstack(feature_parts)


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
        "confusion_matrix": confusion_matrix(labels, predictions, labels=all_labels).tolist(),
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


def extract_structured_feature_importance(model_bundle: dict[str, Any], *, limit: int = 20) -> list[dict[str, Any]]:
    vectorizer: DictVectorizer | None = model_bundle["structured_vectorizer"]
    if vectorizer is None:
        return []
    model: RandomForestClassifier = model_bundle["model"]
    importances = getattr(model, "feature_importances_", None)
    if importances is None:
        return []
    offset = int(model_bundle.get("text_feature_count") or 0)
    structured_names = [str(name) for name in vectorizer.get_feature_names_out()]
    rows = []
    for local_index, name in enumerate(structured_names):
        global_index = offset + local_index
        rows.append({"feature": name, "importance": float(importances[global_index])})
    rows.sort(key=lambda item: item["importance"], reverse=True)
    return rows[:limit]


def build_benchmark_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for case in BENCHMARK_CASES:
        analysis = analyze_resume_job_match(case["resume_text"], case["jd_text"])
        synthetic_like_case = {
            "case_id": case["case_id"],
            "resume_summary": case["resume_text"],
            "job_description_summary": case["jd_text"],
            "target_role": case["scenario"],
            "role_family": "",
            "candidate_stack": "",
            "jd_stack": "",
            "seniority": "",
            "category": "benchmark",
            "fit_label": case["expected_label"],
            "expected_score_range": case["expected_score_range"],
            "missing_critical_skills": analysis.get("missing_skills") or [],
            "skill_overlap": analysis.get("matched_skills") or [],
        }
        rows.append({
            "case_id": case["case_id"],
            "scenario": case["scenario"],
            "expected_label": case["expected_label"],
            "expected_score_range": case["expected_score_range"],
            "text_input": build_matching_feature_text(synthetic_like_case),
            "structured_features": build_hybrid_structured_features(synthetic_like_case, analysis),
            "label": case["expected_label"],
            "source_category": "benchmark",
        })
    return rows


def predict_benchmark_rows(
    config: AblationConfig,
    model_bundle: dict[str, Any],
    benchmark_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    predictions = predict_rows(config, model_bundle, benchmark_rows)
    output = []
    for row, prediction in zip(benchmark_rows, predictions):
        agreement = classify_benchmark_agreement(row["expected_label"], prediction["predicted_label"], prediction["confidence"])
        output.append({
            "case_id": row["case_id"],
            "scenario": row["scenario"],
            "expected_label": row["expected_label"],
            "predicted_label": prediction["predicted_label"],
            "confidence": prediction["confidence"],
            "agreement": agreement,
        })
    return output


def classify_benchmark_agreement(expected_label: str, predicted_label: str, confidence: float) -> str:
    if confidence < 0.45:
        return "needs_review"
    if predicted_label == expected_label:
        return "aligned"
    distance = abs(LABEL_RANK.get(expected_label, -1) - LABEL_RANK.get(predicted_label, -1))
    if distance >= 2:
        return "major_disagreement"
    return "minor_disagreement"


def summarize_metrics(metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        "accuracy": metrics["accuracy"],
        "macro_f1": metrics["macro_f1"],
        "good_to_medium": metrics["good_to_medium"],
        "mismatch_to_medium": metrics["mismatch_to_medium"],
        "weak_errors": metrics["weak_errors"],
    }


def build_report(
    metadata: dict[str, Any],
    ablation_results: dict[str, dict[str, Any]],
    benchmark_results: dict[str, list[dict[str, Any]]],
) -> str:
    ablation_rows = "\n".join(
        "| {title} | {accuracy:.3f} | {macro_f1:.3f} | {good_to_medium} | {mismatch_to_medium} | {weak_errors} |".format(
            title=result["title"],
            **summarize_metrics(result["metrics"]),
        )
        for result in ablation_results.values()
    )
    feature_sections = "\n\n".join(
        build_feature_importance_section(result["title"], result["top_structured_features"])
        for result in ablation_results.values()
    )
    category_sections = "\n\n".join(
        build_category_error_section(result["title"], result["metrics"])
        for result in ablation_results.values()
    )
    benchmark_sections = "\n\n".join(
        build_benchmark_section(ablation_results[key]["title"], rows)
        for key, rows in benchmark_results.items()
    )
    full_metrics = ablation_results["full_hybrid"]["metrics"]
    no_rule_metrics = ablation_results["structured_without_rule_score"]["metrics"]
    core_metrics = ablation_results["structured_core_only"]["metrics"]
    conclusion = build_conclusion(full_metrics, no_rule_metrics, core_metrics)
    return f"""# Phase 9.3 - Hybrid Model Benchmark & Ablation Study

Date: {metadata['created_at']}

## Mục tiêu

Đánh giá Hybrid Matching Model từ Phase 9.2 bằng ablation study để hiểu model đang học được pattern riêng hay chỉ phụ thuộc vào `rule_based_score`. Phase này chỉ là offline evaluation, không thay production `match_score`, `final_score`, database schema, API contract hoặc frontend.

## Ablation table

| Config | Accuracy | Macro F1 | good -> medium | mismatch -> medium | weak errors |
| --- | ---: | ---: | ---: | ---: | ---: |
{ablation_rows}

## Feature importance

{feature_sections}

## Category error analysis

{category_sections}

## U01-U10 behavior

{benchmark_sections}

## Kết luận

{conclusion}

## Có nên productionize không?

Chưa nên. Kết quả ablation hữu ích để hiểu tín hiệu model, nhưng dataset vẫn là synthetic và benchmark U01-U10 vẫn cần human review. Rule-based matcher tiếp tục là source of truth cho user-facing score.

## Recommendation cho Phase 9.4

1. Chạy ablation tương tự trên real beta cases đã ẩn danh khi có đủ dữ liệu.
2. Thử cấu hình không dùng trực tiếp `rule_based_score` nếu muốn giảm teacher leakage.
3. Bổ sung human-reviewed labels cho nhóm role mismatch và same-role different-stack.
4. Chưa tích hợp hybrid/ML model vào production scoring.
"""


def build_dataset_report(metadata: dict[str, Any], ablation_results: dict[str, dict[str, Any]]) -> str:
    rows = "\n".join(
        "| {title} | {accuracy:.3f} | {macro_f1:.3f} | {good_to_medium} | {mismatch_to_medium} | {weak_errors} |".format(
            title=result["title"],
            **summarize_metrics(result["metrics"]),
        )
        for result in ablation_results.values()
    )
    return f"""# Ablation Results V1

Date: {metadata['created_at']}

## Scope

Kết quả ablation offline trên `docs/datasets/synthetic/hybrid_training_dataset.json`. Script không overwrite artifact model hiện có và không thay production scoring.

## Summary

| Config | Accuracy | Macro F1 | good -> medium | mismatch -> medium | weak errors |
| --- | ---: | ---: | ---: | ---: | ---: |
{rows}

## Ghi chú

- `D. Full hybrid` là cấu hình gần nhất với Phase 9.2 hybrid model.
- `B. Structured không có rule_based_score` giúp kiểm tra model còn học được gì khi bỏ teacher score trực tiếp.
- `C. Structured core only` kiểm tra nhóm feature tối thiểu về role/evidence/skill count.
- Không cấu hình nào trong file này được dùng làm production score.
"""


def build_feature_importance_section(title: str, features: list[dict[str, Any]]) -> str:
    if not features:
        return f"### {title}\n\nKhông có structured feature importance để hiển thị."
    rows = "\n".join(
        f"| {item['feature']} | {item['importance']:.5f} |"
        for item in features
    )
    return f"""### {title}

| Feature | Importance |
| --- | ---: |
{rows}"""


def build_category_error_section(title: str, metrics: dict[str, Any]) -> str:
    rows = "\n".join(
        f"| {category} | {value['errors']} | {value['total']} | {value['error_rate']} |"
        for category, value in metrics["category_errors"].items()
    )
    return f"""### {title}

| Category | Errors | Total | Error rate |
| --- | ---: | ---: | ---: |
{rows}"""


def build_benchmark_section(title: str, rows: list[dict[str, Any]]) -> str:
    table_rows = "\n".join(
        f"| {row['case_id']} | {row['expected_label']} | {row['predicted_label']} | {row['confidence']:.3f} | {row['agreement']} |"
        for row in rows
    )
    return f"""### {title}

| Case | Expected | Predicted | Confidence | Agreement |
| --- | --- | --- | ---: | --- |
{table_rows}"""


def build_conclusion(
    full_metrics: dict[str, Any],
    no_rule_metrics: dict[str, Any],
    core_metrics: dict[str, Any],
) -> str:
    full_accuracy = full_metrics["accuracy"]
    no_rule_accuracy = no_rule_metrics["accuracy"]
    core_accuracy = core_metrics["accuracy"]
    if no_rule_accuracy >= full_accuracy - 0.05:
        learning_note = "Model vẫn giữ hiệu năng gần full hybrid khi bỏ `rule_based_score`, cho thấy structured component features có tín hiệu riêng đáng giữ."
    elif core_accuracy >= 0.75:
        learning_note = "Model giảm khi bỏ `rule_based_score`, nhưng core role/evidence features vẫn đủ mạnh để học một phần pattern."
    else:
        learning_note = "Model phụ thuộc đáng kể vào `rule_based_score`; cần cẩn trọng vì có nguy cơ teacher leakage."
    return (
        f"{learning_note}\n\n"
        "Cấu hình đáng giữ để tiếp tục đánh giá là `B. Structured không có rule_based_score` và `D. Full hybrid`. "
        "`D. Full hybrid` có thể dùng làm upper-bound offline, còn `B` phù hợp hơn để kiểm tra khả năng học độc lập trước khi cân nhắc runtime evaluation."
    )


if __name__ == "__main__":
    raise SystemExit(main())
