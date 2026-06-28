"""Export shadow review resolutions sang Label Review Draft offline."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from app.ml.shadow_review_queue import validate_shadow_review_queue


LABELS = {"good", "medium", "weak", "mismatch"}
REQUIRED_EXPORT_FIELDS = {
    "export_id",
    "created_at",
    "source_queue",
    "status",
    "total_items",
    "exported_items",
    "cases",
    "recommendation",
    "approved_for_training",
    "stored_raw_text",
}
REQUIRED_ITEM_FIELDS = {
    "case_id",
    "source",
    "expected_label",
    "resolved_label",
    "original_disagreement_type",
    "severity",
    "reviewer",
    "review_time",
    "resolution_notes",
    "label_confidence",
    "anonymized",
    "approved_for_label_review",
    "approved_for_training",
    "stored_raw_text",
}
MOJIBAKE_PATTERN = re.compile(
    r"\u00c3|\u00c2|\u00e1\u00ba|\u00e1\u00bb|\u00c4|\u00c6|\u00c5|\ufffd|M\?|Kh\?|H\?\?|tr\?|\?\?\?"
)
EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_PATTERN = re.compile(r"(?<!\d)(?:\+?\d[\d\s().-]{8,}\d)(?!\d)")
ISO_TIMESTAMP_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:\+00:00|Z)?")


def read_json(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError(f"File JSON phải là object: {path}")
    return payload


def write_json(path: str | Path, payload: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_no_queue_export(
    *,
    source_queue: str,
    export_id: str,
    created_at: str,
) -> dict[str, Any]:
    export = {
        "export_id": export_id,
        "created_at": created_at,
        "source_queue": source_queue,
        "status": "no_queue",
        "total_items": 0,
        "exported_items": [],
        "cases": [],
        "recommendation": "build shadow review queue first",
        "approved_for_training": False,
        "stored_raw_text": False,
    }
    validate_resolution_export(export)
    return export


def export_shadow_review_resolutions(
    *,
    queue: Mapping[str, Any],
    source_queue: str,
    export_id: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    validate_shadow_review_queue(queue)
    timestamp = created_at or datetime.now(timezone.utc).isoformat()
    resolved_export_id = export_id or f"shadow_resolution_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    exported_items: list[dict[str, Any]] = []
    label_review_cases: list[dict[str, Any]] = []
    case_ids: set[str] = set()
    dataset_version = str(queue.get("dataset_version") or "shadow_review_draft")

    for item in queue.get("items", []):
        if item.get("review_status") != "promoted_to_label_review":
            continue
        exported = _build_exported_item(item)
        case_id = exported["case_id"]
        if case_id in case_ids:
            raise ValueError(f"duplicate case_id trong export: {case_id}.")
        case_ids.add(case_id)
        exported_items.append(exported)
        label_review_cases.append(
            {
                "case_id": case_id,
                "dataset_version": dataset_version,
                "review_status": "UNDER_REVIEW",
                "previous_status": "ANONYMIZED",
                "reviewer": exported["reviewer"],
                "review_time": exported["review_time"],
                "label_confidence": exported["label_confidence"],
                "disagreement_reason": (
                    f"{exported['original_disagreement_type']}: "
                    f"expected={exported['expected_label']}, resolved={exported['resolved_label']}."
                ),
                "notes": exported["resolution_notes"],
                "approved_for_training": False,
                "anonymized": True,
                "source": exported["source"],
                "resolved_label": exported["resolved_label"],
                "approved_for_label_review": True,
                "stored_raw_text": False,
            }
        )

    export = {
        "export_id": resolved_export_id,
        "created_at": timestamp,
        "source_queue": source_queue,
        "status": "ready_for_label_review" if exported_items else "empty",
        "total_items": len(exported_items),
        "exported_items": exported_items,
        "cases": label_review_cases,
        "recommendation": (
            "Chạy Label Review QA trước Dataset Promotion."
            if exported_items
            else "Không có resolved item đủ điều kiện export."
        ),
        "approved_for_training": False,
        "stored_raw_text": False,
    }
    validate_resolution_export(export)
    return export


def validate_resolution_export(export: Mapping[str, Any]) -> None:
    missing = sorted(REQUIRED_EXPORT_FIELDS - export.keys())
    if missing:
        raise ValueError(f"Resolution export thiếu field: {', '.join(missing)}.")
    if not str(export.get("export_id") or "").strip():
        raise ValueError("export_id không được rỗng.")
    if export.get("approved_for_training") is not False:
        raise ValueError("Resolution export yêu cầu approved_for_training=false.")
    if export.get("stored_raw_text") is not False:
        raise ValueError("Resolution export yêu cầu stored_raw_text=false.")
    items = export.get("exported_items")
    cases = export.get("cases")
    if not isinstance(items, list) or not isinstance(cases, list):
        raise ValueError("exported_items và cases phải là list.")
    if export.get("total_items") != len(items) or len(items) != len(cases):
        raise ValueError("total_items không khớp exported_items/cases.")
    case_ids: set[str] = set()
    for index, item in enumerate(items, start=1):
        if not isinstance(item, Mapping):
            raise ValueError(f"Exported item #{index} phải là object.")
        item_missing = sorted(REQUIRED_ITEM_FIELDS - item.keys())
        if item_missing:
            raise ValueError(f"Exported item #{index} thiếu field: {', '.join(item_missing)}.")
        case_id = str(item.get("case_id") or "").strip()
        if not case_id:
            raise ValueError(f"Exported item #{index} thiếu case_id.")
        if case_id in case_ids:
            raise ValueError(f"duplicate case_id trong export: {case_id}.")
        case_ids.add(case_id)
        if not str(item.get("reviewer") or "").strip():
            raise ValueError(f"Exported item #{index} thiếu reviewer.")
        if not str(item.get("resolution_notes") or "").strip():
            raise ValueError(f"Exported item #{index} thiếu resolution_notes.")
        confidence = item.get("label_confidence")
        if not isinstance(confidence, (int, float)) or isinstance(confidence, bool) or not 0 <= float(confidence) <= 1:
            raise ValueError(f"Exported item #{index} có label_confidence không hợp lệ.")
        if item.get("resolved_label") not in LABELS:
            raise ValueError(f"Exported item #{index} có resolved_label không hợp lệ.")
        if item.get("anonymized") is not True:
            raise ValueError(f"Exported item #{index} yêu cầu anonymized=true.")
        if item.get("approved_for_label_review") is not True:
            raise ValueError(f"Exported item #{index} yêu cầu approved_for_label_review=true.")
        if item.get("approved_for_training") is not False:
            raise ValueError("Exported item yêu cầu approved_for_training=false.")
        if item.get("stored_raw_text") is not False:
            raise ValueError("Exported item yêu cầu stored_raw_text=false.")

    for index, case in enumerate(cases, start=1):
        if not isinstance(case, Mapping):
            raise ValueError(f"Label review draft #{index} phải là object.")
        if case.get("approved_for_training") is not False:
            raise ValueError("Label review draft yêu cầu approved_for_training=false.")
        if case.get("anonymized") is not True or case.get("stored_raw_text") is not False:
            raise ValueError("Label review draft vi phạm privacy boundary.")
        if case.get("review_status") != "UNDER_REVIEW":
            raise ValueError("Label review draft phải bắt đầu ở UNDER_REVIEW.")

    serialized = json.dumps(export, ensure_ascii=False)
    if MOJIBAKE_PATTERN.search(serialized):
        raise ValueError("Resolution export có dấu hiệu mojibake.")
    pii_text = ISO_TIMESTAMP_PATTERN.sub("", serialized)
    if EMAIL_PATTERN.search(pii_text) or PHONE_PATTERN.search(pii_text):
        raise ValueError("Resolution export có dấu hiệu PII.")


def _build_exported_item(item: Mapping[str, Any]) -> dict[str, Any]:
    reviewer = str(item.get("reviewer") or "").strip()
    notes = str(item.get("notes") or "").strip()
    review_time = str(item.get("review_time") or "").strip()
    resolved_label = str(item.get("resolved_label") or "").strip()
    confidence = item.get("label_confidence")
    if not reviewer:
        raise ValueError(f"{item.get('case_id')}: reviewer bắt buộc.")
    if not notes:
        raise ValueError(f"{item.get('case_id')}: notes bắt buộc.")
    if not review_time:
        raise ValueError(f"{item.get('case_id')}: review_time bắt buộc.")
    if resolved_label not in LABELS:
        raise ValueError(f"{item.get('case_id')}: resolved_label không hợp lệ.")
    if not isinstance(confidence, (int, float)) or isinstance(confidence, bool) or not 0 <= float(confidence) <= 1:
        raise ValueError(f"{item.get('case_id')}: label_confidence phải nằm trong 0..1.")
    if item.get("anonymized") is not True:
        raise ValueError(f"{item.get('case_id')}: anonymized=true là bắt buộc.")
    if item.get("approved_for_label_review") is not True:
        raise ValueError(f"{item.get('case_id')}: approved_for_label_review=true là bắt buộc.")
    if item.get("approved_for_training") is not False:
        raise ValueError(f"{item.get('case_id')}: approved_for_training phải false.")
    if item.get("stored_raw_text") is not False:
        raise ValueError(f"{item.get('case_id')}: stored_raw_text phải false.")
    return {
        "case_id": str(item.get("case_id") or "").strip(),
        "source": str(item.get("source") or "unknown"),
        "expected_label": item.get("expected_label"),
        "resolved_label": resolved_label,
        "original_disagreement_type": str(item.get("disagreement_type") or ""),
        "severity": str(item.get("severity") or ""),
        "reviewer": reviewer,
        "review_time": review_time,
        "resolution_notes": notes,
        "label_confidence": float(confidence),
        "anonymized": True,
        "approved_for_label_review": True,
        "approved_for_training": False,
        "stored_raw_text": False,
    }
