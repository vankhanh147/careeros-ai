"""Validate label review metadata for CareerOS AI training datasets.

Script này chỉ kiểm tra metadata review offline. Nó không train model,
không thay production scoring và không ghi dữ liệu mới.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.ml.training_infra import parse_label_review_schema, validate_label_review_file


DEFAULT_REVIEW_PATH = BACKEND_DIR / "ml" / "reviews" / "sample_review_cases.json"
DEFAULT_SCHEMA_PATH = BACKEND_DIR / "ml" / "configs" / "label_review_schema.json"


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Validate label review QA pipeline cho CareerOS AI.")
    parser.add_argument("--reviews", default=str(DEFAULT_REVIEW_PATH), help="Đường dẫn file review cases JSON.")
    parser.add_argument("--schema", default=str(DEFAULT_SCHEMA_PATH), help="Đường dẫn label review schema JSON.")
    args = parser.parse_args()

    parse_label_review_schema(Path(args.schema))
    result = validate_label_review_file(Path(args.reviews))
    print_result(result)
    return 1 if result["errors_count"] else 0


def print_result(result: dict) -> None:
    print("CareerOS Label Review QA")
    print("=" * 32)
    print(f"Total cases: {result['total_cases']}")
    print(f"Errors: {result['errors_count']}")
    print(f"Warnings: {result['warnings_count']}")
    print(f"Ready for promotion: {result['ready_for_promotion_count']}")
    print("Status: Ready for promotion" if result["ready_for_promotion"] else "Status: Not ready")

    for item in result["case_results"]:
        print("-" * 32)
        print(f"Case: {item['case_id']} ({item['review_status']})")
        if item["errors"]:
            print("Errors:")
            for error in item["errors"]:
                print(f"  - {error}")
        if item["warnings"]:
            print("Warnings:")
            for warning in item["warnings"]:
                print(f"  - {warning}")
        if not item["errors"] and not item["warnings"]:
            print("Không có lỗi hoặc cảnh báo.")
        print(f"Ready: {item['ready_for_promotion']}")


if __name__ == "__main__":
    raise SystemExit(main())