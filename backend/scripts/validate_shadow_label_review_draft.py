"""Validate Shadow Label Review Draft qua Label Review QA Bridge."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.ml.label_review_bridge import (
    build_no_draft_summary,
    evaluate_label_review_draft,
    read_json,
    write_json,
)


DRAFT_PATH = BACKEND_DIR / "ml" / "reviews" / "shadow_label_review_draft.json"
OUTPUT_PATH = BACKEND_DIR / "ml" / "reports" / "shadow_label_review_draft_qa.json"


def validate_draft(
    *,
    draft_path: Path = DRAFT_PATH,
    output_path: Path = OUTPUT_PATH,
    dry_run: bool = False,
) -> dict:
    if not draft_path.exists():
        summary = build_no_draft_summary(source_draft=str(draft_path))
        return {
            "dry_run": dry_run,
            "summary": summary,
            "output_path": str(output_path),
            "written": False,
        }
    before = draft_path.read_bytes()
    draft = read_json(draft_path)
    summary = evaluate_label_review_draft(
        draft=draft,
        source_draft=str(draft_path),
    )
    if draft_path.read_bytes() != before:
        raise RuntimeError("QA bridge không được sửa Label Review Draft.")
    if not dry_run:
        write_json(output_path, summary)
    return {
        "dry_run": dry_run,
        "summary": summary,
        "output_path": str(output_path),
        "written": not dry_run,
    }


def print_summary(result: dict) -> None:
    summary = result["summary"]
    print("CareerOS AI Label Review Draft QA Bridge")
    print("=" * 50)
    print(f"Status: {summary['status']}")
    print(f"Total cases: {summary['total_cases']}")
    print(f"Errors: {summary['errors_count']}")
    print(f"Warnings: {summary['warnings_count']}")
    print(f"Ready for review: {str(summary['ready_for_review']).lower()}")
    print(f"Ready for promotion: {str(summary['ready_for_promotion']).lower()}")
    print(f"Promotion blockers: {summary['promotion_blockers']}")
    print(f"Recommendation: {summary['recommendation']}")
    print("Draft modified: false")
    print("Promotion allowed: false")
    print("Training allowed: false")
    if result["dry_run"]:
        print("Dry-run: không ghi QA report.")
    elif result["written"]:
        print(f"Đã ghi QA report: {result['output_path']}")
    else:
        print("Không ghi QA report vì chưa có draft.")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Validate shadow Label Review Draft offline.")
    parser.add_argument("--dry-run", action="store_true", help="Không ghi QA report.")
    parser.add_argument("--draft", type=Path, default=DRAFT_PATH, help="Label Review Draft input.")
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH, help="QA report output.")
    args = parser.parse_args()
    try:
        result = validate_draft(
            draft_path=args.draft,
            output_path=args.output,
            dry_run=args.dry_run,
        )
    except Exception as exc:  # noqa: BLE001 - CLI cần báo lỗi rõ.
        print(f"Label Review Draft QA lỗi: {exc}", file=sys.stderr)
        return 1
    print_summary(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
