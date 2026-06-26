"""Promote CareerOS AI dataset metadata to a new version.

This script only manages offline dataset metadata. It does not train models,
change production scoring or modify production APIs.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.ml.training_infra import parse_promotion_config, validate_dataset_promotion


DEFAULT_CONFIG_PATH = BACKEND_DIR / "ml" / "configs" / "dataset_promotion_config.json"
DATASETS_DIR = BACKEND_DIR / "ml" / "datasets"


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Promote dataset metadata cho CareerOS AI.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH), help="Đường dẫn promotion config JSON.")
    parser.add_argument("--dry-run", action="store_true", help="Chỉ in kế hoạch, không tạo metadata mới.")
    args = parser.parse_args()

    config = parse_promotion_config(Path(args.config))
    plan = validate_dataset_promotion(config, datasets_dir=DATASETS_DIR, root_dir=ROOT_DIR)
    print_promotion_plan(plan, dry_run=args.dry_run)

    if args.dry_run:
        return 0

    target_path = Path(plan["target_path"])
    target_path.write_text(
        json.dumps(plan["target_metadata"], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Đã tạo dataset metadata draft: {target_path}")
    return 0


def print_promotion_plan(plan: dict[str, Any], *, dry_run: bool) -> None:
    metadata = plan["target_metadata"]
    print("CareerOS Dataset Promotion Plan")
    print("=" * 40)
    print(f"Mode: {'dry-run' if dry_run else 'write'}")
    print(f"Source: {metadata['promoted_from']}")
    print(f"Target: {metadata['version']}")
    print(f"Target path: {plan['target_path']}")
    print(f"Total cases: {metadata['total_cases']}")
    print(f"Synthetic cases: {metadata['synthetic_cases']}")
    print(f"Benchmark cases: {metadata['benchmark_cases']}")
    print(f"Beta cases: {metadata['beta_cases']}")
    print(f"Status: {metadata['status']}")
    print(f"Production safe: {metadata['production_safe']}")
    if dry_run:
        print("Dry-run: không tạo file metadata mới.")


if __name__ == "__main__":
    raise SystemExit(main())