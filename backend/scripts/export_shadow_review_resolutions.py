"""Export resolved shadow review items thành Label Review Draft."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.ml.shadow_review_resolution import (
    build_no_queue_export,
    export_shadow_review_resolutions,
    read_json,
    write_json,
)


QUEUE_PATH = BACKEND_DIR / "ml" / "reviews" / "shadow_review_queue.json"
OUTPUT_PATH = BACKEND_DIR / "ml" / "reviews" / "shadow_label_review_draft.json"


def export_resolutions(
    *,
    queue_path: Path = QUEUE_PATH,
    output_path: Path = OUTPUT_PATH,
    dry_run: bool = False,
    now: datetime | None = None,
) -> dict:
    timestamp = now or datetime.now(timezone.utc)
    export_id = f"shadow_resolution_{timestamp.strftime('%Y%m%dT%H%M%SZ')}"
    if not queue_path.exists():
        export = build_no_queue_export(
            source_queue=str(queue_path),
            export_id=export_id,
            created_at=timestamp.isoformat(),
        )
        return {
            "dry_run": dry_run,
            "export": export,
            "output_path": str(output_path),
            "written": False,
        }
    queue = read_json(queue_path)
    export = export_shadow_review_resolutions(
        queue=queue,
        source_queue=str(queue_path),
        export_id=export_id,
        created_at=timestamp.isoformat(),
    )
    if not dry_run:
        write_json(output_path, export)
    return {
        "dry_run": dry_run,
        "export": export,
        "output_path": str(output_path),
        "written": not dry_run,
    }


def print_export(result: dict) -> None:
    export = result["export"]
    print("CareerOS AI Shadow Review Resolution Export")
    print("=" * 52)
    print(f"Status: {export['status']}")
    print(f"Export ID: {export['export_id']}")
    print(f"Total items: {export['total_items']}")
    print(f"Recommendation: {export['recommendation']}")
    print("Approved for training: false")
    print("Stored raw text: false")
    if result["dry_run"]:
        print("Dry-run: không ghi label review draft.")
    elif result["written"]:
        print(f"Đã ghi draft: {result['output_path']}")
    else:
        print("Không ghi draft vì chưa có shadow review queue.")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Export shadow review resolutions offline.")
    parser.add_argument("--dry-run", action="store_true", help="Không ghi label review draft.")
    parser.add_argument("--queue", type=Path, default=QUEUE_PATH, help="Shadow review queue input.")
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH, help="Label review draft output.")
    args = parser.parse_args()
    try:
        result = export_resolutions(
            queue_path=args.queue,
            output_path=args.output,
            dry_run=args.dry_run,
        )
    except Exception as exc:  # noqa: BLE001 - CLI cần báo lỗi rõ.
        print(f"Shadow resolution export lỗi: {exc}", file=sys.stderr)
        return 1
    print_export(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
