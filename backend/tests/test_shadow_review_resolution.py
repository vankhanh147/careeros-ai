import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.ml.training_infra import validate_label_review_case

from app.ml.shadow_review_resolution import (
    export_shadow_review_resolutions,
    validate_resolution_export,
)
from scripts.export_shadow_review_resolutions import export_resolutions


def write_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def queue_item(case_id="U04", status="promoted_to_label_review"):
    return {
        "item_id": f"queue-test:{case_id}",
        "case_id": case_id,
        "source": "benchmark",
        "expected_label": "weak",
        "rule_label": "weak",
        "candidate_label": "good",
        "hybrid_label": "weak",
        "candidate_confidence": 0.81,
        "disagreement_type": "benchmark_anomaly",
        "severity": "high",
        "review_reason": "Benchmark bất đồng.",
        "recommended_action": "Review thủ công.",
        "review_status": status,
        "reviewer": "reviewer-test" if status != "pending" else "",
        "notes": "Đã kiểm tra role mismatch và evidence.",
        "resolved_label": "weak",
        "review_time": "2026-06-28T00:00:00+00:00",
        "label_confidence": 0.9,
        "anonymized": True,
        "approved_for_label_review": status == "promoted_to_label_review",
        "approved_for_training": False,
        "stored_raw_text": False,
    }


def sample_queue(items=None):
    selected = items if items is not None else [queue_item(), queue_item("SYN001", "resolved")]
    return {
        "queue_id": "queue-test",
        "created_at": "2026-06-28T00:00:00+00:00",
        "source_report": "shadow_summary.json",
        "status": "ready_for_human_review",
        "total_items": len(selected),
        "items": selected,
        "severity_summary": {"low": 0, "medium": 0, "high": 1},
        "disagreement_summary": {"benchmark_anomaly": 1},
        "recommendation": "Review.",
        "approved_for_training": False,
        "stored_raw_text": False,
    }


def build_export(queue=None):
    return export_shadow_review_resolutions(
        queue=queue or sample_queue(),
        source_queue="shadow_review_queue.json",
        export_id="export-test",
        created_at="2026-06-28T00:00:00+00:00",
    )


def test_no_queue_does_not_crash(tmp_path):
    result = export_resolutions(
        queue_path=tmp_path / "missing.json",
        output_path=tmp_path / "draft.json",
        dry_run=True,
        now=datetime(2026, 6, 28, tzinfo=timezone.utc),
    )
    assert result["export"]["status"] == "no_queue"
    assert result["export"]["recommendation"] == "build shadow review queue first"
    assert result["written"] is False


def test_only_promoted_items_are_exported():
    export = build_export()
    assert export["total_items"] == 1
    assert export["exported_items"][0]["case_id"] == "U04"
    assert export["cases"][0]["review_status"] == "UNDER_REVIEW"
    assert export["cases"][0]["approved_for_training"] is False
    assert validate_label_review_case(export["cases"][0]) == []


def test_missing_reviewer_rejected():
    item = queue_item()
    item["reviewer"] = ""
    with pytest.raises(ValueError, match="reviewer"):
        build_export(sample_queue([item]))


def test_missing_notes_rejected():
    item = queue_item()
    item["notes"] = ""
    with pytest.raises(ValueError, match="notes"):
        build_export(sample_queue([item]))


def test_approved_for_training_true_rejected():
    item = queue_item()
    item["approved_for_training"] = True
    with pytest.raises(ValueError, match="approved_for_training"):
        build_export(sample_queue([item]))


def test_stored_raw_text_true_rejected():
    item = queue_item()
    item["stored_raw_text"] = True
    with pytest.raises(ValueError, match="stored_raw_text=false"):
        build_export(sample_queue([item]))


def test_duplicate_case_id_rejected():
    first = queue_item("U04")
    second = queue_item("U04")
    second["item_id"] = "queue-test:U04-duplicate"
    with pytest.raises(ValueError, match="duplicate case_id"):
        build_export(sample_queue([first, second]))


def test_dry_run_does_not_write(tmp_path):
    queue_path = tmp_path / "queue.json"
    output_path = tmp_path / "draft.json"
    write_json(queue_path, sample_queue())
    result = export_resolutions(
        queue_path=queue_path,
        output_path=output_path,
        dry_run=True,
        now=datetime(2026, 6, 28, tzinfo=timezone.utc),
    )
    assert result["written"] is False
    assert not output_path.exists()


def test_write_mode_creates_label_review_draft(tmp_path):
    queue_path = tmp_path / "queue.json"
    output_path = tmp_path / "shadow_label_review_draft.json"
    write_json(queue_path, sample_queue())
    result = export_resolutions(
        queue_path=queue_path,
        output_path=output_path,
        dry_run=False,
        now=datetime(2026, 6, 28, tzinfo=timezone.utc),
    )
    assert result["written"] is True
    assert output_path.exists()
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    validate_resolution_export(payload)
    assert payload["approved_for_training"] is False
    assert payload["stored_raw_text"] is False
