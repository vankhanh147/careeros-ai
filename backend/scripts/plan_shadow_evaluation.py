"""Lập Shadow Evaluation plan offline, không chạy inference."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.ml.shadow_evaluation import create_shadow_plan, load_shadow_config, write_json


CONFIG_PATH = BACKEND_DIR / "ml" / "configs" / "shadow_evaluation_config.json"
OUTPUT_PATH = BACKEND_DIR / "ml" / "reports" / "shadow_evaluation_plan.json"


def plan_shadow_evaluation(
    *,
    config_path: Path = CONFIG_PATH,
    workspace: Path = ROOT_DIR,
    output_path: Path = OUTPUT_PATH,
    dry_run: bool = False,
) -> dict:
    config = load_shadow_config(config_path)
    plan = create_shadow_plan(config=config, workspace=workspace)
    if not dry_run:
        write_json(output_path, plan)
    return {
        "dry_run": dry_run,
        "plan": plan,
        "output_path": str(output_path),
        "written": not dry_run,
    }


def print_plan(result: dict) -> None:
    plan = result["plan"]
    print("CareerOS AI Shadow Evaluation Plan")
    print("=" * 44)
    print(f"Requested enabled: {str(plan['requested_enabled']).lower()}")
    print(f"Requested mode: {plan['requested_mode']}")
    print(f"Effective enabled: {str(plan['effective_enabled']).lower()}")
    print(f"Effective mode: {plan['effective_mode']}")
    print(f"Candidate status: {plan['candidate_status']}")
    print(f"Safety outcome: {plan['outcome']}")
    for item in plan["safety_checks"]:
        print(f"  [{item['status']}] {item['check_id']}: {item['message']}")
    for warning in plan["warnings"]:
        print(f"  [WARNING] {warning}")
    print(f"Recommendation: {plan['recommendation']}")
    print("Runtime activation allowed: false")
    if result["dry_run"]:
        print("Dry-run: không ghi shadow plan.")
    else:
        print(f"Đã ghi plan: {result['output_path']}")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Lập shadow evaluation plan offline.")
    parser.add_argument("--dry-run", action="store_true", help="Không ghi shadow plan.")
    parser.add_argument("--config", type=Path, default=CONFIG_PATH, help="Shadow config JSON.")
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH, help="Output plan JSON.")
    args = parser.parse_args()
    try:
        result = plan_shadow_evaluation(
            config_path=args.config,
            output_path=args.output,
            dry_run=args.dry_run,
        )
    except Exception as exc:  # noqa: BLE001 - CLI cần báo lỗi rõ ràng.
        print(f"Shadow planning lỗi: {exc}", file=sys.stderr)
        return 1
    print_plan(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
