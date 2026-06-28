import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.ml.shadow_review_queue import (
    build_shadow_review_queue,
    validate_shadow_review_queue,
)
from scripts.build_shadow_review_queue import build_queue


def write_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def fake_shadow_summary():
    return {
        "status": "completed",
        "comparison_records": [
            {
                "case_id": "SYN001",
                "source": "synthetic",
                "expected_label": "good",
                "rule_label": "good",
                "hybrid_label": "good",
                "ml_label": "medium",
                "ml_confidence": 0.42,
                "review_required": True,
            },
            {
                "case_id": "U04",
                "source": "benchmark",
                "expected_label": "weak",
                "rule_label": "weak",
                "hybrid_label": "weak",
                "ml_label": "good",
                "ml_confidence": 0.81,
                "review_required": True,
            },
            {
                "case_id": "SYN002",
                "source": "synthetic",
                "expected_label": "medium",
                "rule_label": "medium",
                "hybrid_label": "medium",
                "ml_label": "medium",
                "ml_confidence": 0.9,
                "review_required": False,
            },
        ],
    }


def test_no_source_report_does_not_crash(tmp_path):
    result = build_queue(
        source_path=tmp_path / "missing.json",
        output_path=tmp_path / "queue.json",
        dry_run=True,
        now=datetime(2026, 6, 28, tzinfo=timezone.utc),
    )
    assert result["queue"]["status"] == "no_source_report"
    assert result["queue"]["recommendation"] == "run shadow harness write mode first"
    assert result["written"] is False


def test_build_queue_from_shadow_summary():
    queue = build_shadow_review_queue(
        report=fake_shadow_summary(),
        source_report="shadow_summary.json",
        queue_id="queue-test",
        created_at="2026-06-28T00:00:00+00:00",
    )
    assert queue["status"] == "ready_for_human_review"
    assert queue["total_items"] == 2
    assert queue["stored_raw_text"] is False
    assert queue["approved_for_training"] is False


def test_only_review_required_records_are_selected():
    queue = build_shadow_review_queue(
        report=fake_shadow_summary(),
        source_report="shadow_summary.json",
        queue_id="queue-test",
        created_at="2026-06-28T00:00:00+00:00",
    )
    assert {item["case_id"] for item in queue["items"]} == {"SYN001", "U04"}


def test_severity_classification():
    queue = build_shadow_review_queue(
        report=fake_shadow_summary(),
        source_report="shadow_summary.json",
        queue_id="queue-test",
        created_at="2026-06-28T00:00:00+00:00",
    )
    by_case = {item["case_id"]: item for item in queue["items"]}
    assert by_case["SYN001"]["disagreement_type"] == "low_confidence"
    assert by_case["SYN001"]["severity"] == "medium"
    assert by_case["U04"]["disagreement_type"] == "benchmark_anomaly"
    assert by_case["U04"]["severity"] == "high"


def test_validator_rejects_stored_raw_text_true():
    queue = build_shadow_review_queue(
        report=fake_shadow_summary(),
        source_report="shadow_summary.json",
        queue_id="queue-test",
        created_at="2026-06-28T00:00:00+00:00",
    )
    queue["items"][0]["stored_raw_text"] = True
    with pytest.raises(ValueError, match="stored_raw_text=false"):
        validate_shadow_review_queue(queue)


def test_dry_run_does_not_write(tmp_path):
    source = tmp_path / "shadow_summary.json"
    output = tmp_path / "shadow_review_queue.json"
    write_json(source, fake_shadow_summary())
    result = build_queue(
        source_path=source,
        output_path=output,
        dry_run=True,
        now=datetime(2026, 6, 28, tzinfo=timezone.utc),
    )
    assert result["written"] is False
    assert not output.exists()


def test_write_mode_creates_queue(tmp_path):
    source = tmp_path / "shadow_summary.json"
    output = tmp_path / "shadow_review_queue.json"
    write_json(source, fake_shadow_summary())
    result = build_queue(
        source_path=source,
        output_path=output,
        dry_run=False,
        now=datetime(2026, 6, 28, tzinfo=timezone.utc),
    )
    assert result["written"] is True
    assert output.exists()
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["total_items"] == 2
    assert payload["approved_for_training"] is False
