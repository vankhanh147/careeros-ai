"""Build Shadow Disagreement Review Queue offline."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.ml.shadow_review_queue import (
    build_no_source_queue,
    build_shadow_review_queue,
    read_json,
    write_json,
)


SOURCE_PATH = BACKEND_DIR / "ml" / "reports" / "shadow_summary.json"
OUTPUT_PATH = BACKEND_DIR / "ml" / "reviews" / "shadow_review_queue.json"


def build_queue(
    *,
    source_path: Path = SOURCE_PATH,
    output_path: Path = OUTPUT_PATH,
    dry_run: bool = False,
    now: datetime | None = None,
) -> dict:
    timestamp = now or datetime.now(timezone.utc)
    queue_id = f"shadow_review_{timestamp.strftime('%Y%m%dT%H%M%SZ')}"
    if not source_path.exists():
        queue = build_no_source_queue(
            source_report=str(source_path),
            queue_id=queue_id,
            created_at=timestamp.isoformat(),
        )
        return {
            "dry_run": dry_run,
            "queue": queue,
            "output_path": str(output_path),
            "written": False,
        }
    report = read_json(source_path)
    queue = build_shadow_review_queue(
        report=report,
        source_report=str(source_path),
        queue_id=queue_id,
        created_at=timestamp.isoformat(),
    )
    if not dry_run:
        write_json(output_path, queue)
    return {
        "dry_run": dry_run,
        "queue": queue,
        "output_path": str(output_path),
        "written": not dry_run,
    }


def print_queue(result: dict) -> None:
    queue = result["queue"]
    print("CareerOS AI Shadow Disagreement Review Queue")
    print("=" * 52)
    print(f"Status: {queue['status']}")
    print(f"Queue ID: {queue['queue_id']}")
    print(f"Total items: {queue['total_items']}")
    print(f"Severity: {queue.get('severity_summary', {})}")
    print(f"Recommendation: {queue['recommendation']}")
    print("Approved for training: false")
    print("Stored raw text: false")
    if result["dry_run"]:
        print("Dry-run: không ghi review queue.")
    elif result["written"]:
        print(f"Đã ghi queue: {result['output_path']}")
    else:
        print("Không ghi queue vì chưa có source report.")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Build shadow disagreement review queue offline.")
    parser.add_argument("--dry-run", action="store_true", help="Không ghi queue.")
    parser.add_argument("--source", type=Path, default=SOURCE_PATH, help="Shadow summary input.")
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH, help="Review queue output.")
    args = parser.parse_args()
    try:
        result = build_queue(
            source_path=args.source,
            output_path=args.output,
            dry_run=args.dry_run,
        )
    except Exception as exc:  # noqa: BLE001 - CLI cần báo lỗi rõ.
        print(f"Shadow review queue lỗi: {exc}", file=sys.stderr)
        return 1
    print_queue(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
