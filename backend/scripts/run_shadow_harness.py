"""Chạy Offline Shadow Evaluation Harness, không tác động production."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.ml.shadow_evaluation import load_shadow_config, resolve_workspace_path
from app.ml.shadow_harness import (
    evaluate_shadow_cases,
    load_candidate_predictor,
    load_training_cases,
    write_json,
)


DATASET_PATH = BACKEND_DIR / "ml" / "datasets" / "training_dataset_v3.json"
SHADOW_CONFIG_PATH = BACKEND_DIR / "ml" / "configs" / "shadow_evaluation_config.json"
OUTPUT_PATH = BACKEND_DIR / "ml" / "reports" / "shadow_summary.json"


def run_shadow_harness(
    *,
    dataset_path: Path = DATASET_PATH,
    config_path: Path = SHADOW_CONFIG_PATH,
    registry_path: Path | None = None,
    output_path: Path = OUTPUT_PATH,
    workspace: Path = ROOT_DIR,
    dry_run: bool = False,
) -> dict:
    dataset, cases = load_training_cases(dataset_path)
    config = load_shadow_config(config_path)
    configured_registry = str(config.get("candidate_registry_path") or "").strip()
    selected_registry = registry_path
    if selected_registry is None and configured_registry:
        selected_registry = resolve_workspace_path(workspace, configured_registry)
    candidate_predictor, candidate_metadata = load_candidate_predictor(
        registry_path=selected_registry,
        workspace=workspace,
    )
    report = evaluate_shadow_cases(
        dataset_metadata=dataset,
        cases=cases,
        candidate_predictor=candidate_predictor,
        candidate_metadata=candidate_metadata,
    )
    if not dry_run:
        write_json(output_path, report)
    return {
        "dry_run": dry_run,
        "report": report,
        "output_path": str(output_path),
        "written": not dry_run,
    }


def print_summary(result: dict) -> None:
    report = result["report"]
    print("CareerOS AI Offline Shadow Evaluation Harness")
    print("=" * 52)
    print(f"Status: {report['status']}")
    print(f"Dataset version: {report['dataset_version']}")
    print(f"Total cases: {report['total_cases']}")
    print(f"Benchmark cases: {report['benchmark_cases']}")
    print(f"Candidate available: {str(report['candidate']['available']).lower()}")
    print(f"Agreement rate: {report['agreement_rate']}")
    print(f"Disagreement rate: {report['disagreement_rate']}")
    print(f"Needs human review: {report['review_required_count']}")
    print(f"Recommendation: {report['recommendation']}")
    print("Production score source: rule_based")
    print("Production change allowed: false")
    if result["dry_run"]:
        print("Dry-run: không ghi shadow summary.")
    else:
        print(f"Đã ghi report: {result['output_path']}")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Chạy offline shadow evaluation harness.")
    parser.add_argument("--dry-run", action="store_true", help="Không ghi shadow summary.")
    parser.add_argument("--dataset", type=Path, default=DATASET_PATH, help="Training dataset artifact.")
    parser.add_argument("--config", type=Path, default=SHADOW_CONFIG_PATH, help="Shadow config.")
    parser.add_argument("--registry", type=Path, help="Candidate registry tùy chọn.")
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH, help="Shadow summary output.")
    args = parser.parse_args()
    try:
        result = run_shadow_harness(
            dataset_path=args.dataset,
            config_path=args.config,
            registry_path=args.registry,
            output_path=args.output,
            dry_run=args.dry_run,
        )
    except Exception as exc:  # noqa: BLE001 - CLI cần báo lỗi rõ.
        print(f"Shadow harness lỗi: {exc}", file=sys.stderr)
        return 1
    print_summary(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
