"""Build Dataset Promotion Plan từ Label Review Draft QA evidence."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.ml.dataset_promotion_bridge import (
    build_dataset_promotion_plan,
    build_no_qa_plan,
    read_json,
    write_json,
)


QA_PATH = BACKEND_DIR / "ml" / "reports" / "shadow_label_review_draft_qa.json"
MANIFEST_PATH = BACKEND_DIR / "ml" / "datasets" / "training_dataset_manifest.json"
OUTPUT_PATH = BACKEND_DIR / "ml" / "reports" / "dataset_promotion_plan.json"


def build_plan(
    *,
    qa_path: Path = QA_PATH,
    manifest_path: Path = MANIFEST_PATH,
    output_path: Path = OUTPUT_PATH,
    dry_run: bool = False,
) -> dict:
    if not qa_path.exists():
        plan = build_no_qa_plan(source_qa_report=str(qa_path))
        return {
            "dry_run": dry_run,
            "plan": plan,
            "output_path": str(output_path),
            "written": False,
        }
    qa_before = qa_path.read_bytes()
    utf8_valid, bom_free = validate_utf8_file(qa_path)
    qa_report = read_json(qa_path)
    source_draft_value = str(qa_report.get("source_draft") or "").strip()
    if not source_draft_value:
        raise ValueError("QA report thiếu source_draft.")
    source_draft = Path(source_draft_value)
    if not source_draft.is_absolute():
        source_draft = BACKEND_DIR.parent / source_draft
    if not source_draft.exists():
        raise ValueError(f"Không tìm thấy source draft: {source_draft}")
    draft_before = source_draft.read_bytes()
    draft_utf8, draft_bom_free = validate_utf8_file(source_draft)
    if not manifest_path.exists():
        raise ValueError(f"Không tìm thấy dataset manifest: {manifest_path}")
    manifest_before = manifest_path.read_bytes()
    manifest_utf8, manifest_bom_free = validate_utf8_file(manifest_path)
    draft = read_json(source_draft)
    manifest = read_json(manifest_path)
    existing_plan = read_json(output_path) if output_path.exists() else None
    plan = build_dataset_promotion_plan(
        qa_report=qa_report,
        draft=draft,
        manifest=manifest,
        source_qa_report=str(qa_path),
        source_draft=str(source_draft),
        existing_plan=existing_plan,
        utf8_valid=utf8_valid and draft_utf8 and manifest_utf8,
        bom_free=bom_free and draft_bom_free and manifest_bom_free,
    )
    if (
        qa_path.read_bytes() != qa_before
        or source_draft.read_bytes() != draft_before
        or manifest_path.read_bytes() != manifest_before
    ):
        raise RuntimeError("Promotion Planning Bridge không được sửa input.")
    if not dry_run:
        write_json(output_path, plan)
    return {
        "dry_run": dry_run,
        "plan": plan,
        "output_path": str(output_path),
        "written": not dry_run,
    }


def validate_utf8_file(path: Path) -> tuple[bool, bool]:
    data = path.read_bytes()
    bom_free = not data.startswith(b"\xef\xbb\xbf")
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return False, bom_free
    return True, bom_free


def print_plan(result: dict) -> None:
    plan = result["plan"]
    print("CareerOS AI Dataset Promotion Planning Bridge")
    print("=" * 54)
    print(f"Status: {plan['status']}")
    print(f"Total cases: {plan['total_cases']}")
    print(f"Promotion ready: {plan['promotion_ready']}")
    print(f"Blocked cases: {plan['blocked_cases']}")
    print(f"Target dataset version: {plan['target_dataset_version']}")
    print(f"Estimated dataset size: {plan['estimated_dataset_size']}")
    print(f"Blockers: {plan['blockers']}")
    print(f"Recommendation: {plan['recommendation']}")
    print(f"Promotion allowed: {str(plan['promotion_allowed']).lower()}")
    print("Promotion executed: false")
    print("Training allowed: false")
    if result["dry_run"]:
        print("Dry-run: không ghi promotion plan.")
    elif result["written"]:
        print(f"Đã ghi plan: {result['output_path']}")
    else:
        print("Không ghi plan vì chưa có QA report.")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Build Dataset Promotion Plan offline.")
    parser.add_argument("--dry-run", action="store_true", help="Không ghi promotion plan.")
    parser.add_argument("--qa", type=Path, default=QA_PATH, help="Label Review QA report.")
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH, help="Current dataset manifest.")
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH, help="Promotion plan output.")
    args = parser.parse_args()
    try:
        result = build_plan(
            qa_path=args.qa,
            manifest_path=args.manifest,
            output_path=args.output,
            dry_run=args.dry_run,
        )
    except Exception as exc:  # noqa: BLE001 - CLI cần báo lỗi rõ.
        print(f"Dataset promotion planning lỗi: {exc}", file=sys.stderr)
        return 1
    print_plan(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
