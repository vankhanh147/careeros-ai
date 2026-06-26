"""Review một model registry draft theo Model Registry Review Gate."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.ml.model_review import (
    apply_review_result,
    load_model_review_config,
    resolve_workspace_path,
    review_registry,
)


CONFIG_PATH = BACKEND_DIR / "ml" / "configs" / "model_review_config.json"
REGISTRY_DIR = BACKEND_DIR / "ml" / "registry"


def run_review(
    *,
    config_path: Path = CONFIG_PATH,
    workspace: Path = ROOT_DIR,
    registry_path: Path | None = None,
    dry_run: bool = False,
) -> dict:
    config = load_model_review_config(config_path)
    selected_registry = registry_path or resolve_workspace_path(workspace, str(config["registry_path"]))
    result = review_registry(
        registry_path=selected_registry,
        config=config,
        workspace=workspace,
        registry_dir=selected_registry.parent,
    )
    if not dry_run and selected_registry.exists():
        apply_review_result(selected_registry, result)
        result["registry_updated"] = True
    else:
        result["registry_updated"] = False
    result["dry_run"] = dry_run
    return result


def print_result(result: dict) -> None:
    print("CareerOS AI Model Registry Review Gate")
    print("=" * 48)
    print(f"Registry: {result['registry_path']}")
    print(f"Model version: {result.get('model_version') or 'không xác định'}")
    print(f"Kết quả: {result['outcome']}")
    if result["issues"]:
        print("Chi tiết:")
        for issue in result["issues"]:
            print(f"  [{issue['level']}] {issue['code']}: {issue['message']}")
    else:
        print("  [PASS] Không phát hiện lỗi hoặc cảnh báo.")
    print(f"Recommendation: {result['recommendation']}")
    if result["dry_run"]:
        print("Dry-run: registry không được thay đổi.")
    else:
        print(f"Registry status đã cập nhật: {result['target_status']}")
    print("Production boundary: production_safe=false.")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Review model registry draft offline.")
    parser.add_argument("--dry-run", action="store_true", help="Chỉ review, không cập nhật registry.")
    parser.add_argument("--registry", type=Path, help="Registry JSON cần review; mặc định lấy từ config.")
    args = parser.parse_args()
    try:
        result = run_review(registry_path=args.registry, dry_run=args.dry_run)
    except Exception as exc:  # noqa: BLE001 - CLI cần báo lỗi rõ.
        print(f"Review gate lỗi: {exc}", file=sys.stderr)
        return 1
    print_result(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
