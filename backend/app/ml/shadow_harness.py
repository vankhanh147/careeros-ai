"""Offline Shadow Evaluation Harness.

Harness chỉ chạy trên dataset artifact offline. Comparison records không chứa
raw CV/JD text và không ảnh hưởng production matcher hoặc API response.
"""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

from app.ml.features import build_matching_feature_text


LABELS = {"good", "medium", "weak", "mismatch"}
LABEL_RANK = {"mismatch": 0, "weak": 1, "medium": 2, "good": 3}
RulePredictor = Callable[[Mapping[str, Any]], Mapping[str, Any]]
CandidatePredictor = Callable[[Mapping[str, Any]], Mapping[str, Any]]


def read_json(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError(f"File JSON phải là object: {path}")
    return payload


def write_json(path: str | Path, payload: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_training_cases(path: str | Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    dataset = read_json(path)
    cases = dataset.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("Training dataset thiếu cases hoặc đang rỗng.")
    normalized: list[dict[str, Any]] = []
    for index, case in enumerate(cases, start=1):
        if not isinstance(case, dict):
            raise ValueError(f"Case #{index} phải là JSON object.")
        case_id = str(case.get("case_id") or "").strip()
        expected = str(case.get("fit_label") or "").strip()
        if not case_id:
            raise ValueError(f"Case #{index} thiếu case_id.")
        if expected not in LABELS:
            raise ValueError(f"{case_id}: fit_label không hợp lệ.")
        normalized.append(dict(case))
    return dataset, normalized


def load_candidate_predictor(
    *,
    registry_path: Path | None,
    workspace: Path,
) -> tuple[CandidatePredictor | None, dict[str, Any]]:
    if registry_path is None or not registry_path.exists():
        return None, {
            "available": False,
            "status": "not_found",
            "model_version": None,
            "reason": "Không có candidate registry.",
        }
    registry = read_json(registry_path)
    if registry.get("status") != "candidate" or registry.get("production_safe") is not False:
        return None, {
            "available": False,
            "status": str(registry.get("status") or "invalid"),
            "model_version": registry.get("model_version"),
            "reason": "Registry chưa phải candidate an toàn.",
        }
    artifact_paths = registry.get("artifact_paths")
    if not isinstance(artifact_paths, dict):
        return None, {
            "available": False,
            "status": "invalid",
            "model_version": registry.get("model_version"),
            "reason": "Registry thiếu artifact_paths.",
        }
    model_path = _resolve_path(workspace, artifact_paths.get("model"))
    vectorizer_path = _resolve_path(workspace, artifact_paths.get("vectorizer"))
    if model_path is None or vectorizer_path is None or not model_path.exists() or not vectorizer_path.exists():
        return None, {
            "available": False,
            "status": "artifact_missing",
            "model_version": registry.get("model_version"),
            "reason": "Thiếu model hoặc vectorizer artifact.",
        }
    try:
        import joblib

        model = joblib.load(model_path)
        vectorizer = joblib.load(vectorizer_path)
    except Exception as exc:  # pragma: no cover - defensive artifact fallback
        return None, {
            "available": False,
            "status": "load_failed",
            "model_version": registry.get("model_version"),
            "reason": f"Không load được candidate artifact: {exc.__class__.__name__}.",
        }

    def predict(case: Mapping[str, Any]) -> Mapping[str, Any]:
        features = vectorizer.transform([build_matching_feature_text(case)])
        predicted_label = str(model.predict(features)[0])
        confidence = None
        probabilities: dict[str, float] = {}
        if hasattr(model, "predict_proba"):
            values = model.predict_proba(features)[0]
            classes = [str(label) for label in model.classes_]
            probabilities = {
                label: round(float(value), 4)
                for label, value in sorted(zip(classes, values), key=lambda item: item[0])
            }
            confidence = round(float(max(values)), 4)
        return {
            "predicted_label": predicted_label,
            "confidence": confidence,
            "label_probabilities": probabilities,
        }

    return predict, {
        "available": True,
        "status": "candidate",
        "model_version": registry.get("model_version"),
        "reason": None,
    }


def evaluate_shadow_cases(
    *,
    dataset_metadata: Mapping[str, Any],
    cases: list[dict[str, Any]],
    rule_predictor: RulePredictor | None = None,
    candidate_predictor: CandidatePredictor | None = None,
    candidate_metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    baseline = rule_predictor or _default_rule_predictor
    candidate_info = dict(candidate_metadata or {})
    candidate_available = candidate_predictor is not None
    records: list[dict[str, Any]] = []
    agreement_count = 0
    disagreement_count = 0
    candidate_better = 0
    rule_better = 0
    inconclusive = 0
    review_required_count = 0
    confidences: list[float] = []
    confusion: Counter[str] = Counter()

    for case in cases:
        expected_label = str(case["fit_label"])
        rule_result = dict(baseline(case))
        rule_score = _number(rule_result.get("rule_based_score", rule_result.get("match_score")))
        rule_label = _valid_label(rule_result.get("rule_label")) or label_from_score(rule_score)
        hybrid_score = _optional_number(
            rule_result.get("hybrid_score", rule_result.get("hybrid_score_candidate"))
        )
        hybrid_label = (
            _valid_label(rule_result.get("hybrid_label"))
            or (label_from_score(hybrid_score) if hybrid_score is not None else rule_label)
        )

        ml_label: str | None = None
        ml_confidence: float | None = None
        comparison_outcome = "baseline_only"
        review_required = False
        if candidate_predictor is not None:
            prediction = dict(candidate_predictor(case))
            ml_label = _valid_label(prediction.get("predicted_label"))
            ml_confidence = _optional_number(prediction.get("confidence"))
            if ml_confidence is not None:
                confidences.append(ml_confidence)
            if ml_label is None:
                comparison_outcome = "inconclusive"
                inconclusive += 1
                review_required = True
            else:
                all_agree = rule_label == ml_label == hybrid_label
                if all_agree:
                    agreement_count += 1
                else:
                    disagreement_count += 1
                comparison_outcome = classify_model_outcome(
                    expected_label=expected_label,
                    rule_label=rule_label,
                    candidate_label=ml_label,
                )
                if comparison_outcome == "candidate_better":
                    candidate_better += 1
                elif comparison_outcome == "rule_better":
                    rule_better += 1
                else:
                    inconclusive += 1
                review_required = not all_agree or ml_confidence is None or ml_confidence < 0.5
                confusion[f"{expected_label}->{ml_label}"] += 1
        if review_required:
            review_required_count += 1

        records.append(
            {
                "case_id": str(case["case_id"]),
                "source": str(case.get("source") or "unknown"),
                "expected_label": expected_label,
                "rule_based_score": round(rule_score, 2),
                "rule_label": rule_label,
                "hybrid_label": hybrid_label,
                "ml_label": ml_label,
                "ml_confidence": ml_confidence,
                "comparison_outcome": comparison_outcome,
                "review_required": review_required,
                "stored_raw_text": False,
            }
        )

    total = len(records)
    if candidate_available:
        status = "completed"
        recommendation = (
            "Review các disagreement trước khi tạo deployment decision mới."
            if disagreement_count
            else "Candidate đồng thuận trên dataset offline; vẫn giữ production baseline."
        )
        agreement_rate: float | None = round(agreement_count / total, 4) if total else 0.0
        disagreement_rate: float | None = round(disagreement_count / total, 4) if total else 0.0
    else:
        status = "baseline_only"
        recommendation = "keep baseline"
        agreement_rate = None
        disagreement_rate = None

    source_counts = Counter(record["source"] for record in records)
    return {
        "report_version": "offline_shadow_summary_v1",
        "status": status,
        "dataset_version": dataset_metadata.get("dataset_version"),
        "candidate": {
            "available": candidate_available,
            "model_version": candidate_info.get("model_version"),
            "status": candidate_info.get("status", "injected" if candidate_available else "not_found"),
            "reason": candidate_info.get("reason"),
        },
        "total_cases": total,
        "benchmark_cases": source_counts.get("benchmark", 0),
        "source_distribution": dict(sorted(source_counts.items())),
        "agreement_count": agreement_count,
        "agreement_rate": agreement_rate,
        "disagreement_count": disagreement_count,
        "disagreement_rate": disagreement_rate,
        "candidate_better": candidate_better,
        "rule_better": rule_better,
        "inconclusive": inconclusive,
        "average_confidence": round(sum(confidences) / len(confidences), 4) if confidences else None,
        "review_required_count": review_required_count,
        "confusion_summary": dict(sorted(confusion.items())),
        "comparison_records": records,
        "recommendation": recommendation,
        "production_score_source": "rule_based",
        "production_change_allowed": False,
        "stored_raw_text": False,
    }


def classify_model_outcome(
    *,
    expected_label: str,
    rule_label: str,
    candidate_label: str,
) -> str:
    rule_distance = abs(LABEL_RANK[rule_label] - LABEL_RANK[expected_label])
    candidate_distance = abs(LABEL_RANK[candidate_label] - LABEL_RANK[expected_label])
    if candidate_distance < rule_distance:
        return "candidate_better"
    if rule_distance < candidate_distance:
        return "rule_better"
    return "inconclusive"


def label_from_score(score: float) -> str:
    if score >= 75:
        return "good"
    if score >= 50:
        return "medium"
    if score >= 25:
        return "weak"
    return "mismatch"


def _default_rule_predictor(case: Mapping[str, Any]) -> Mapping[str, Any]:
    from app.services.resume_job_matcher import analyze_resume_job_match

    result = analyze_resume_job_match(
        str(case.get("resume_summary") or ""),
        str(case.get("job_description_summary") or ""),
    )
    hybrid = result.get("hybrid_evaluation")
    hybrid_score = hybrid.get("hybrid_score_candidate") if isinstance(hybrid, dict) else None
    return {
        "rule_based_score": result["match_score"],
        "hybrid_score_candidate": hybrid_score,
    }


def _resolve_path(workspace: Path, value: Any) -> Path | None:
    if not value:
        return None
    path = Path(str(value))
    return path if path.is_absolute() else workspace / path


def _valid_label(value: Any) -> str | None:
    label = str(value or "")
    return label if label in LABELS else None


def _number(value: Any) -> float:
    if isinstance(value, bool):
        return float(int(value))
    if isinstance(value, (int, float)):
        return float(value)
    return 0.0


def _optional_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return float(int(value))
    if isinstance(value, (int, float)):
        return float(value)
    return None
