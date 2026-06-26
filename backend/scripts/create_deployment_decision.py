"""Tạo Deployment Decision Record offline cho model candidate."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.ml.model_comparison import (
    build_decision_record,
    compare_candidate_with_baseline,
    read_json,
    resolve_workspace_path,
    validate_decision_record,
    write_json,
)
from app.ml.model_review import load_model_review_config


REVIEW_CONFIG_PATH = BACKEND_DIR / "ml" / "configs" / "model_review_config.json"
DECISIONS_DIR = BACKEND_DIR / "ml" / "decisions"
BASELINE = {
    "baseline_version": "rule_based_matcher_v2.1",
    "description": "Matcher rule-based production hiện tại, explainable và deterministic.",
    "known_limitations": [
        "Semantic signal chỉ là metadata tùy chọn.",
        "Production score chưa dùng trainable model.",
    ],
}


def load_candidate_and_evaluation(
    *,
    registry_path: Path,
    workspace: Path,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    if not registry_path.exists():
        return None, None
    candidate = read_json(registry_path)
    artifact_paths = candidate.get("artifact_paths")
    evaluation = None
    if isinstance(artifact_paths, dict) and artifact_paths.get("evaluation_report"):
        evaluation_path = resolve_workspace_path(workspace, str(artifact_paths["evaluation_report"]))
        if evaluation_path.exists():
            evaluation = read_json(evaluation_path)
    return candidate, evaluation


def create_decision(
    *,
    workspace: Path = ROOT_DIR,
    registry_path: Path | None = None,
    review_result_path: Path | None = None,
    reviewer: str = "",
    decisions_dir: Path = DECISIONS_DIR,
    dry_run: bool = False,
    now: datetime | None = None,
) -> dict[str, Any]:
    review_config = load_model_review_config(REVIEW_CONFIG_PATH)
    selected_registry = registry_path or resolve_workspace_path(
        workspace, str(review_config["registry_path"])
    )
    candidate, evaluation = load_candidate_and_evaluation(
        registry_path=selected_registry,
        workspace=workspace,
    )
    if review_result_path is not None and not review_result_path.exists():
        raise ValueError(f"Không tìm thấy model review result: {review_result_path}")
    review_result = read_json(review_result_path) if review_result_path is not None else None
    if candidate is None and not dry_run:
        raise ValueError("Write mode yêu cầu model candidate và dataset_hash hợp lệ.")
    if candidate is not None and candidate.get("status") != "candidate":
        raise ValueError("Candidate registry phải có status=candidate.")

    comparison = compare_candidate_with_baseline(
        candidate=candidate,
        evaluation=evaluation,
        review_result=review_result,
        baseline=BASELINE,
        minimum_accuracy=float(review_config["minimum_accuracy"]),
        minimum_macro_f1=float(review_config["minimum_macro_f1"]),
    )
    timestamp = now or datetime.now(timezone.utc)
    model_part = comparison.get("candidate_model_version") or "no_candidate"
    decision_id = f"decision_{model_part}_{timestamp.strftime('%Y%m%dT%H%M%SZ')}"
    effective_reviewer = reviewer.strip() if not dry_run else reviewer.strip() or "dry-run"
    record = build_decision_record(
        comparison=comparison,
        candidate=candidate,
        reviewer=effective_reviewer,
        decision_id=decision_id,
        decision_time=timestamp.isoformat(),
    )
    validate_decision_record(
        record,
        allow_no_candidate=candidate is None,
        require_reviewer=not dry_run,
    )
    output_path = decisions_dir / f"{decision_id}.json"
    if not dry_run:
        if output_path.exists():
            raise ValueError(f"Decision record đã tồn tại: {output_path}")
        write_json(output_path, record)
    return {
        "dry_run": dry_run,
        "candidate_found": candidate is not None,
        "registry_path": str(selected_registry),
        "output_path": str(output_path),
        "comparison": comparison,
        "record": record,
        "written": not dry_run,
    }


def print_result(result: dict[str, Any]) -> None:
    comparison = result["comparison"]
    record = result["record"]
    print("CareerOS AI Model Comparison & Deployment Decision")
    print("=" * 56)
    print(f"Candidate: {record['candidate_model_version'] or 'không có'}")
    print(f"Baseline: {record['baseline_version']}")
    print(f"Comparison: {comparison['comparison_status']}")
    print(f"Risk: {record['risk_level']}")
    print(f"Decision: {record['decision']}")
    print(f"Rationale: {record['rationale']}")
    print("Production change allowed: false")
    if result["dry_run"]:
        print("Dry-run: không ghi decision record.")
    else:
        print(f"Đã ghi: {result['output_path']}")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Tạo Deployment Decision Record offline.")
    parser.add_argument("--dry-run", action="store_true", help="Không ghi decision record.")
    parser.add_argument("--registry", type=Path, help="Registry candidate; mặc định lấy từ review config.")
    parser.add_argument("--review-result", type=Path, help="Review result JSON tùy chọn.")
    parser.add_argument("--reviewer", default="", help="Reviewer bắt buộc trong write mode.")
    args = parser.parse_args()
    try:
        result = create_decision(
            registry_path=args.registry,
            review_result_path=args.review_result,
            reviewer=args.reviewer,
            dry_run=args.dry_run,
        )
    except Exception as exc:  # noqa: BLE001 - CLI cần trả lỗi rõ ràng.
        print(f"Deployment decision lỗi: {exc}", file=sys.stderr)
        return 1
    print_result(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
