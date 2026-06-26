"""Chạy Release Readiness Checklist và ghi audit trail offline."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.ml.model_review import load_model_review_config, resolve_workspace_path
from app.ml.release_audit import build_release_audit, read_json, validate_audit_record, write_json


REVIEW_CONFIG_PATH = BACKEND_DIR / "ml" / "configs" / "model_review_config.json"
MANIFEST_PATH = BACKEND_DIR / "ml" / "datasets" / "training_dataset_manifest.json"
DATASET_PATH = BACKEND_DIR / "ml" / "datasets" / "training_dataset_v3.json"
TRAINING_CONFIG_PATH = BACKEND_DIR / "ml" / "configs" / "training_config.json"
DECISIONS_DIR = BACKEND_DIR / "ml" / "decisions"
AUDITS_DIR = BACKEND_DIR / "ml" / "audits"


def find_latest_decision(decisions_dir: Path) -> Path | None:
    files = sorted(decisions_dir.glob("*.json"), key=lambda path: path.stat().st_mtime, reverse=True)
    return files[0] if files else None


def run_audit(
    *,
    workspace: Path = ROOT_DIR,
    registry_path: Path | None = None,
    decision_path: Path | None = None,
    quality_evidence_path: Path | None = None,
    reviewer: str = "",
    audits_dir: Path = AUDITS_DIR,
    dry_run: bool = False,
    now: datetime | None = None,
) -> dict:
    review_config = load_model_review_config(REVIEW_CONFIG_PATH)
    selected_registry = registry_path or resolve_workspace_path(
        workspace, str(review_config["registry_path"])
    )
    selected_decision = decision_path or find_latest_decision(DECISIONS_DIR)
    if quality_evidence_path is not None and not quality_evidence_path.exists():
        raise ValueError(f"Không tìm thấy quality evidence: {quality_evidence_path}")
    quality_evidence = read_json(quality_evidence_path) if quality_evidence_path else None
    timestamp = now or datetime.now(timezone.utc)
    model_part = selected_registry.stem if selected_registry.exists() else "no_candidate"
    audit_id = f"audit_{model_part}_{timestamp.strftime('%Y%m%dT%H%M%SZ')}"
    effective_reviewer = reviewer.strip() if not dry_run else reviewer.strip() or "dry-run"
    record = build_release_audit(
        workspace=workspace,
        manifest_path=MANIFEST_PATH,
        dataset_path=DATASET_PATH,
        training_config_path=TRAINING_CONFIG_PATH,
        registry_path=selected_registry,
        decision_path=selected_decision,
        quality_evidence=quality_evidence,
        reviewer=effective_reviewer,
        audit_id=audit_id,
        timestamp=timestamp.isoformat(),
    )
    validate_audit_record(record, require_reviewer=not dry_run)
    output_path = audits_dir / f"{audit_id}.json"
    if not dry_run:
        if output_path.exists():
            raise ValueError(f"Audit record đã tồn tại: {output_path}")
        write_json(output_path, record)
    return {
        "dry_run": dry_run,
        "record": record,
        "output_path": str(output_path),
        "written": not dry_run,
    }


def print_result(result: dict) -> None:
    record = result["record"]
    summary = record["checklist_summary"]
    print("CareerOS AI Release Readiness Audit")
    print("=" * 48)
    print(f"Audit ID: {record['audit_id']}")
    print(f"Kết quả: {summary['outcome']}")
    print(
        f"Checklist: PASS={summary['counts']['PASS']} "
        f"WARNING={summary['counts']['WARNING']} FAIL={summary['counts']['FAIL']}"
    )
    for item in record["checklist_result"]:
        print(f"  [{item['status']}] {item['check_id']}: {item['message']}")
    print(f"Recommendation: {summary['recommendation']}")
    print("Production change allowed: false")
    if result["dry_run"]:
        print("Dry-run: không ghi audit record.")
    else:
        print(f"Đã ghi audit: {result['output_path']}")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Chạy release readiness audit offline.")
    parser.add_argument("--dry-run", action="store_true", help="Không ghi audit record.")
    parser.add_argument("--registry", type=Path, help="Registry candidate tùy chọn.")
    parser.add_argument("--decision", type=Path, help="Deployment decision record tùy chọn.")
    parser.add_argument("--quality-evidence", type=Path, help="JSON evidence cho pytest/compileall/pip check.")
    parser.add_argument("--reviewer", default="", help="Reviewer bắt buộc trong write mode.")
    args = parser.parse_args()
    try:
        result = run_audit(
            registry_path=args.registry,
            decision_path=args.decision,
            quality_evidence_path=args.quality_evidence,
            reviewer=args.reviewer,
            dry_run=args.dry_run,
        )
    except Exception as exc:  # noqa: BLE001 - CLI cần trả lỗi rõ ràng.
        print(f"Release audit lỗi: {exc}", file=sys.stderr)
        return 1
    print_result(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
