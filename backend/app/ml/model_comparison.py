"""So sánh model candidate với production baseline ở chế độ offline.

Module không inference, không deploy và không thay đổi production scoring.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


COMPARISON_STATUSES = {"better", "worse", "inconclusive"}
RISK_LEVELS = {"low", "medium", "high"}
DECISIONS = {"keep_baseline", "keep_shadow", "approve_candidate", "reject_candidate"}
REQUIRED_DECISION_FIELDS = {
    "decision_id",
    "candidate_model_version",
    "baseline_version",
    "dataset_version",
    "dataset_hash",
    "comparison_summary",
    "risk_level",
    "decision",
    "reviewer",
    "decision_time",
    "rationale",
    "required_followups",
    "production_change_allowed",
}


def read_json(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError(f"File JSON phải là object: {path}")
    return payload


def write_json(path: str | Path, payload: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def resolve_workspace_path(workspace: Path, value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else workspace / path


def compare_candidate_with_baseline(
    *,
    candidate: dict[str, Any] | None,
    evaluation: dict[str, Any] | None,
    review_result: dict[str, Any] | None,
    baseline: dict[str, Any],
    minimum_accuracy: float = 0.7,
    minimum_macro_f1: float = 0.7,
) -> dict[str, Any]:
    if candidate is None:
        return {
            "comparison_status": "inconclusive",
            "risk_level": "medium",
            "recommendation": "keep_baseline",
            "candidate_model_version": None,
            "baseline_version": baseline["baseline_version"],
            "baseline_description": baseline.get("description", ""),
            "baseline_known_limitations": baseline.get("known_limitations", []),
            "candidate_metrics": {},
            "benchmark_evidence": False,
            "known_limitations": ["Không có model candidate để so sánh."],
            "rationale": "Candidate registry không tồn tại hoặc chưa có candidate khả dụng.",
            "required_followups": [
                "Chạy Training Job Contract để tạo registry draft.",
                "Đưa registry draft qua Model Registry Review Gate.",
            ],
        }

    if candidate.get("status") != "candidate":
        raise ValueError("Candidate registry phải có status=candidate.")
    if candidate.get("production_safe") is not False:
        raise ValueError("Candidate registry phải giữ production_safe=false.")
    dataset_hash = str(candidate.get("dataset_hash") or "").strip()
    if not dataset_hash:
        raise ValueError("Candidate registry thiếu dataset_hash.")

    metrics = _extract_metrics(candidate, evaluation)
    accuracy = metrics.get("accuracy")
    macro_f1 = metrics.get("macro_f1")
    metrics_valid = _valid_score(accuracy) and _valid_score(macro_f1)
    metrics_pass = (
        metrics_valid
        and float(accuracy) >= minimum_accuracy
        and float(macro_f1) >= minimum_macro_f1
    )
    benchmark_results = (evaluation or {}).get("benchmark_results")
    benchmark_evidence = bool(benchmark_results)
    review_outcome = _extract_review_outcome(candidate, review_result)
    review_pass = review_outcome == "PASS"
    review_acceptable = review_outcome in {"PASS", "WARNING"}
    limitations = _collect_limitations(candidate, evaluation, benchmark_evidence, review_outcome)

    if not metrics_valid or not metrics_pass:
        return {
            "comparison_status": "worse",
            "risk_level": "high",
            "recommendation": "reject_candidate",
            "candidate_model_version": candidate.get("model_version"),
            "baseline_version": baseline["baseline_version"],
            "baseline_description": baseline.get("description", ""),
            "baseline_known_limitations": baseline.get("known_limitations", []),
            "candidate_metrics": metrics,
            "benchmark_evidence": benchmark_evidence,
            "known_limitations": limitations,
            "rationale": "Candidate không đạt metrics gate tối thiểu hoặc metrics không hợp lệ.",
            "required_followups": [
                "Phân tích lỗi model trước khi tạo version mới.",
                "Không thay baseline production hiện tại.",
            ],
        }

    if not benchmark_evidence or not review_acceptable:
        return {
            "comparison_status": "inconclusive",
            "risk_level": "high" if not review_acceptable else "medium",
            "recommendation": "keep_shadow",
            "candidate_model_version": candidate.get("model_version"),
            "baseline_version": baseline["baseline_version"],
            "baseline_description": baseline.get("description", ""),
            "baseline_known_limitations": baseline.get("known_limitations", []),
            "candidate_metrics": metrics,
            "benchmark_evidence": benchmark_evidence,
            "known_limitations": limitations,
            "rationale": "Metrics đạt ngưỡng nhưng chưa đủ benchmark/review evidence để kết luận tốt hơn baseline.",
            "required_followups": [
                "Hoàn tất benchmark U01-U10 và ghi kết quả vào evaluation report.",
                "Xác nhận Model Registry Review Gate ở mức PASS hoặc WARNING.",
            ],
        }

    high_confidence_metrics = float(accuracy) >= 0.8 and float(macro_f1) >= 0.8
    if high_confidence_metrics and review_pass:
        recommendation = "approve_candidate"
        risk_level = "low"
        rationale = (
            "Candidate đạt metrics gate, có benchmark evidence và review PASS; "
            "đủ điều kiện ghi nhận cho deployment decision tương lai."
        )
    else:
        recommendation = "keep_shadow"
        risk_level = "medium"
        rationale = (
            "Candidate có tín hiệu tốt hơn nhưng vẫn nên giữ ở chế độ shadow để thu thập thêm bằng chứng."
        )
    return {
        "comparison_status": "better",
        "risk_level": risk_level,
        "recommendation": recommendation,
        "candidate_model_version": candidate.get("model_version"),
        "baseline_version": baseline["baseline_version"],
        "baseline_description": baseline.get("description", ""),
        "baseline_known_limitations": baseline.get("known_limitations", []),
        "candidate_metrics": metrics,
        "benchmark_evidence": benchmark_evidence,
        "known_limitations": limitations,
        "rationale": rationale,
        "required_followups": [
            "Giữ production scoring hiện tại cho tới phase runtime/deployment riêng.",
            "Review beta evidence trước mọi thay đổi production.",
        ],
    }


def build_decision_record(
    *,
    comparison: dict[str, Any],
    candidate: dict[str, Any] | None,
    reviewer: str,
    decision_id: str,
    decision_time: str | None = None,
) -> dict[str, Any]:
    record = {
        "decision_id": decision_id,
        "candidate_model_version": comparison.get("candidate_model_version"),
        "baseline_version": comparison["baseline_version"],
        "dataset_version": candidate.get("dataset_version") if candidate else None,
        "dataset_hash": candidate.get("dataset_hash") if candidate else None,
        "comparison_summary": {
            "comparison_status": comparison["comparison_status"],
            "baseline_description": comparison.get("baseline_description", ""),
            "baseline_known_limitations": comparison.get("baseline_known_limitations", []),
            "candidate_metrics": comparison["candidate_metrics"],
            "benchmark_evidence": comparison["benchmark_evidence"],
            "known_limitations": comparison["known_limitations"],
        },
        "risk_level": comparison["risk_level"],
        "decision": comparison["recommendation"],
        "reviewer": reviewer,
        "decision_time": decision_time or datetime.now(timezone.utc).isoformat(),
        "rationale": comparison["rationale"],
        "required_followups": comparison["required_followups"],
        "production_change_allowed": False,
    }
    validate_decision_record(record, allow_no_candidate=candidate is None)
    return record


def validate_decision_record(
    record: dict[str, Any],
    *,
    allow_no_candidate: bool = False,
    require_reviewer: bool = True,
) -> None:
    missing = sorted(REQUIRED_DECISION_FIELDS - record.keys())
    if missing:
        raise ValueError(f"Decision record thiếu field bắt buộc: {', '.join(missing)}.")
    if record["risk_level"] not in RISK_LEVELS:
        raise ValueError("risk_level không hợp lệ.")
    if record["decision"] not in DECISIONS:
        raise ValueError("decision không hợp lệ.")
    if record["production_change_allowed"] is not False:
        raise ValueError("Phase 10.6 yêu cầu production_change_allowed=false.")
    if require_reviewer and not str(record.get("reviewer") or "").strip():
        raise ValueError("Write mode yêu cầu reviewer.")
    if not allow_no_candidate:
        if not str(record.get("candidate_model_version") or "").strip():
            raise ValueError("Decision record thiếu candidate_model_version.")
        if not str(record.get("dataset_hash") or "").strip():
            raise ValueError("Decision record thiếu dataset_hash.")
    elif record["decision"] != "keep_baseline":
        raise ValueError("No-candidate mode chỉ cho phép keep_baseline.")


def _extract_metrics(
    candidate: dict[str, Any],
    evaluation: dict[str, Any] | None,
) -> dict[str, Any]:
    evaluation_metrics = (evaluation or {}).get("metrics")
    if isinstance(evaluation_metrics, dict):
        return {
            "accuracy": evaluation_metrics.get("accuracy"),
            "macro_f1": evaluation_metrics.get("macro_f1"),
        }
    return {
        "accuracy": candidate.get("accuracy"),
        "macro_f1": candidate.get("macro_f1"),
    }


def _extract_review_outcome(
    candidate: dict[str, Any],
    review_result: dict[str, Any] | None,
) -> str | None:
    if review_result:
        return str(review_result.get("outcome") or "") or None
    history = candidate.get("review_history")
    if isinstance(history, list) and history:
        return str(history[-1].get("outcome") or "") or None
    return None


def _collect_limitations(
    candidate: dict[str, Any],
    evaluation: dict[str, Any] | None,
    benchmark_evidence: bool,
    review_outcome: str | None,
) -> list[str]:
    limitations: list[str] = []
    if not benchmark_evidence:
        limitations.append("Chưa có benchmark evidence trong evaluation report.")
    if not review_outcome:
        limitations.append("Chưa có model review outcome.")
    notes = (evaluation or {}).get("known_limitations")
    if isinstance(notes, list):
        limitations.extend(str(item) for item in notes if str(item).strip())
    candidate_notes = str(candidate.get("notes") or "").strip()
    if candidate_notes:
        limitations.append(candidate_notes)
    return list(dict.fromkeys(limitations))


def _valid_score(value: Any) -> bool:
    return isinstance(value, (int, float)) and 0 <= float(value) <= 1
