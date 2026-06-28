"""Build và validate Shadow Disagreement Review Queue offline."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


SEVERITIES = {"low", "medium", "high"}
REVIEW_STATUSES = {
    "pending",
    "under_review",
    "resolved",
    "rejected",
    "promoted_to_label_review",
}
DISAGREEMENT_TYPES = {
    "rule_vs_candidate",
    "rule_vs_expected",
    "candidate_vs_expected",
    "low_confidence",
    "benchmark_anomaly",
    "no_candidate",
}
LABEL_RANK = {"mismatch": 0, "weak": 1, "medium": 2, "good": 3}
REQUIRED_QUEUE_FIELDS = {
    "queue_id",
    "created_at",
    "source_report",
    "status",
    "total_items",
    "items",
    "recommendation",
    "stored_raw_text",
}
REQUIRED_ITEM_FIELDS = {
    "item_id",
    "case_id",
    "source",
    "expected_label",
    "rule_label",
    "candidate_label",
    "hybrid_label",
    "disagreement_type",
    "severity",
    "review_reason",
    "recommended_action",
    "review_status",
    "reviewer",
    "notes",
    "approved_for_label_review",
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


def build_no_source_queue(
    *,
    source_report: str,
    queue_id: str,
    created_at: str,
) -> dict[str, Any]:
    queue = {
        "queue_id": queue_id,
        "created_at": created_at,
        "source_report": source_report,
        "status": "no_source_report",
        "total_items": 0,
        "items": [],
        "severity_summary": {"low": 0, "medium": 0, "high": 0},
        "disagreement_summary": {},
        "recommendation": "run shadow harness write mode first",
        "approved_for_training": False,
        "stored_raw_text": False,
    }
    validate_shadow_review_queue(queue)
    return queue


def build_shadow_review_queue(
    *,
    report: Mapping[str, Any],
    source_report: str,
    queue_id: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    timestamp = created_at or datetime.now(timezone.utc).isoformat()
    resolved_queue_id = queue_id or f"shadow_review_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    records = report.get("comparison_records")
    if not isinstance(records, list):
        raise ValueError("Shadow summary thiếu comparison_records.")

    items: list[dict[str, Any]] = []
    for record in records:
        if not isinstance(record, Mapping) or record.get("review_required") is not True:
            continue
        case_id = str(record.get("case_id") or "").strip()
        disagreement_type = classify_disagreement_type(record)
        severity = classify_severity(record, disagreement_type)
        reason, action = build_review_guidance(record, disagreement_type, severity)
        items.append(
            {
                "item_id": f"{resolved_queue_id}:{case_id}",
                "case_id": case_id,
                "source": str(record.get("source") or "unknown"),
                "expected_label": _nullable_label(record.get("expected_label")),
                "rule_label": _nullable_label(record.get("rule_label")),
                "candidate_label": _nullable_label(record.get("ml_label")),
                "hybrid_label": _nullable_label(record.get("hybrid_label")),
                "candidate_confidence": _nullable_number(record.get("ml_confidence")),
                "disagreement_type": disagreement_type,
                "severity": severity,
                "review_reason": reason,
                "recommended_action": action,
                "review_status": "pending",
                "reviewer": "",
                "notes": "",
                "approved_for_label_review": False,
                "approved_for_training": False,
                "stored_raw_text": False,
            }
        )

    severity_summary = {
        severity: sum(item["severity"] == severity for item in items)
        for severity in ("low", "medium", "high")
    }
    disagreement_summary = {
        kind: sum(item["disagreement_type"] == kind for item in items)
        for kind in sorted(DISAGREEMENT_TYPES)
        if any(item["disagreement_type"] == kind for item in items)
    }
    queue = {
        "queue_id": resolved_queue_id,
        "created_at": timestamp,
        "source_report": source_report,
        "status": "ready_for_human_review" if items else "empty",
        "total_items": len(items),
        "items": items,
        "severity_summary": severity_summary,
        "disagreement_summary": disagreement_summary,
        "recommendation": (
            "Review high severity trước, sau đó mới cân nhắc promote sang label review pipeline."
            if items
            else "Không có disagreement record cần human review."
        ),
        "approved_for_training": False,
        "stored_raw_text": False,
    }
    validate_shadow_review_queue(queue)
    return queue


def classify_disagreement_type(record: Mapping[str, Any]) -> str:
    expected = _nullable_label(record.get("expected_label"))
    rule = _nullable_label(record.get("rule_label"))
    candidate = _nullable_label(record.get("ml_label"))
    hybrid = _nullable_label(record.get("hybrid_label"))
    confidence = _nullable_number(record.get("ml_confidence"))
    source = str(record.get("source") or "")

    if candidate is None:
        return "no_candidate"
    if source == "benchmark" and len({expected, rule, candidate, hybrid}) > 1:
        return "benchmark_anomaly"
    if confidence is None or confidence < 0.5:
        return "low_confidence"
    if expected and candidate != expected:
        return "candidate_vs_expected"
    if expected and rule != expected:
        return "rule_vs_expected"
    if rule != candidate:
        return "rule_vs_candidate"
    return "rule_vs_candidate"


def classify_severity(record: Mapping[str, Any], disagreement_type: str) -> str:
    expected = _nullable_label(record.get("expected_label"))
    rule = _nullable_label(record.get("rule_label"))
    candidate = _nullable_label(record.get("ml_label"))
    confidence = _nullable_number(record.get("ml_confidence"))
    source = str(record.get("source") or "")

    candidate_distance = _label_distance(expected, candidate)
    rule_distance = _label_distance(expected, rule)
    if source == "benchmark" and disagreement_type == "benchmark_anomaly":
        return "high"
    if candidate_distance >= 2 or rule_distance >= 2:
        return "high"
    if disagreement_type == "no_candidate":
        return "medium"
    if confidence is None or confidence < 0.5:
        return "medium"
    if candidate_distance == 1 or rule_distance == 1 or rule != candidate:
        return "medium"
    return "low"


def build_review_guidance(
    record: Mapping[str, Any],
    disagreement_type: str,
    severity: str,
) -> tuple[str, str]:
    labels = (
        f"expected={record.get('expected_label')}, rule={record.get('rule_label')}, "
        f"candidate={record.get('ml_label')}, hybrid={record.get('hybrid_label')}."
    )
    reasons = {
        "no_candidate": "Case được đánh dấu review nhưng chưa có candidate prediction.",
        "benchmark_anomaly": "Benchmark case có bất đồng giữa expected, rule, candidate hoặc hybrid.",
        "low_confidence": "Candidate confidence thấp hoặc không có confidence.",
        "candidate_vs_expected": "Candidate label khác expected label.",
        "rule_vs_expected": "Rule-based label khác expected label.",
        "rule_vs_candidate": "Rule-based và candidate label bất đồng.",
    }
    action = (
        "Review evidence và expected label thủ công; không promote trực tiếp thành training label."
        if severity != "high"
        else "Ưu tiên review thủ công, kiểm tra role/stack/evidence và benchmark expectation trước."
    )
    return f"{reasons[disagreement_type]} {labels}", action


def validate_shadow_review_queue(queue: Mapping[str, Any]) -> None:
    missing = sorted(REQUIRED_QUEUE_FIELDS - queue.keys())
    if missing:
        raise ValueError(f"Review queue thiếu field: {', '.join(missing)}.")
    if not str(queue.get("queue_id") or "").strip():
        raise ValueError("queue_id không được rỗng.")
    if queue.get("stored_raw_text") is not False:
        raise ValueError("Review queue yêu cầu stored_raw_text=false.")
    items = queue.get("items")
    if not isinstance(items, list):
        raise ValueError("items phải là list.")
    if queue.get("total_items") != len(items):
        raise ValueError("total_items không khớp số items.")
    item_ids: set[str] = set()
    for index, item in enumerate(items, start=1):
        if not isinstance(item, Mapping):
            raise ValueError(f"Queue item #{index} phải là object.")
        item_missing = sorted(REQUIRED_ITEM_FIELDS - item.keys())
        if item_missing:
            raise ValueError(f"Queue item #{index} thiếu field: {', '.join(item_missing)}.")
        item_id = str(item.get("item_id") or "").strip()
        if not item_id:
            raise ValueError(f"Queue item #{index} thiếu item_id.")
        if item_id in item_ids:
            raise ValueError(f"item_id bị trùng: {item_id}.")
        item_ids.add(item_id)
        if not str(item.get("case_id") or "").strip():
            raise ValueError(f"Queue item #{index} thiếu case_id.")
        if item.get("severity") not in SEVERITIES:
            raise ValueError(f"Queue item #{index} có severity không hợp lệ.")
        if item.get("review_status") not in REVIEW_STATUSES:
            raise ValueError(f"Queue item #{index} có review_status không hợp lệ.")
        if item.get("disagreement_type") not in DISAGREEMENT_TYPES:
            raise ValueError(f"Queue item #{index} có disagreement_type không hợp lệ.")
        if item.get("stored_raw_text") is not False:
            raise ValueError("Queue item yêu cầu stored_raw_text=false.")
        if item.get("approved_for_label_review") not in {True, False}:
            raise ValueError("approved_for_label_review phải là boolean.")
        if item.get("approved_for_training") is not False:
            raise ValueError("Shadow queue không được approved_for_training.")
        status = str(item["review_status"])
        reviewer = str(item.get("reviewer") or "").strip()
        if status in {"under_review", "resolved", "rejected", "promoted_to_label_review"} and not reviewer:
            raise ValueError(f"Queue item #{index} yêu cầu reviewer.")
        if item.get("approved_for_label_review") is True and status not in {
            "resolved",
            "promoted_to_label_review",
        }:
            raise ValueError("approved_for_label_review chỉ hợp lệ sau human review.")

    serialized = json.dumps(queue, ensure_ascii=False)
    if MOJIBAKE_PATTERN.search(serialized):
        raise ValueError("Review queue có dấu hiệu mojibake.")
    pii_text = ISO_TIMESTAMP_PATTERN.sub("", serialized)
    if EMAIL_PATTERN.search(pii_text) or PHONE_PATTERN.search(pii_text):
        raise ValueError("Review queue có dấu hiệu PII.")


def _nullable_label(value: Any) -> str | None:
    label = str(value or "")
    return label if label in LABEL_RANK else None


def _nullable_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return float(int(value))
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _label_distance(left: str | None, right: str | None) -> int:
    if left is None or right is None:
        return 0
    return abs(LABEL_RANK[left] - LABEL_RANK[right])
