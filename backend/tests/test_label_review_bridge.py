import json
from pathlib import Path

from app.ml.label_review_bridge import evaluate_label_review_draft
from scripts.validate_shadow_label_review_draft import validate_draft


def write_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def valid_case():
    return {
        "case_id": "U04",
        "dataset_version": "shadow_review_draft",
        "review_status": "UNDER_REVIEW",
        "previous_status": "ANONYMIZED",
        "reviewer": "reviewer-test",
        "review_time": "2026-06-28T00:00:00+00:00",
        "label_confidence": 0.9,
        "disagreement_reason": "benchmark_anomaly: expected=weak, resolved=weak.",
        "notes": "Đã kiểm tra role mismatch.",
        "approved_for_training": False,
        "anonymized": True,
        "source": "benchmark",
        "resolved_label": "weak",
        "approved_for_label_review": True,
        "stored_raw_text": False,
    }


def draft_with(cases):
    return {
        "export_id": "export-test",
        "created_at": "2026-06-28T00:00:00+00:00",
        "source_queue": "queue.json",
        "status": "ready_for_label_review",
        "total_items": len(cases),
        "exported_items": [],
        "cases": cases,
        "recommendation": "Review.",
        "approved_for_training": False,
        "stored_raw_text": False,
    }


def test_no_draft_does_not_crash(tmp_path):
    result = validate_draft(
        draft_path=tmp_path / "missing.json",
        output_path=tmp_path / "qa.json",
        dry_run=True,
    )
    assert result["summary"]["status"] == "no_draft"
    assert result["summary"]["recommendation"] == "run shadow review resolution export first"
    assert result["written"] is False


def test_valid_draft_runs_existing_validator():
    summary = evaluate_label_review_draft(
        draft=draft_with([valid_case()]),
        source_draft="draft.json",
    )
    assert summary["errors_count"] == 0
    assert summary["ready_for_review"] is True
    assert summary["ready_for_promotion"] is False
    assert summary["status"] == "ready_for_review"


def test_invalid_draft_returns_errors():
    case = valid_case()
    case["reviewer"] = ""
    summary = evaluate_label_review_draft(
        draft=draft_with([case]),
        source_draft="draft.json",
    )
    assert summary["errors_count"] > 0
    assert summary["not_ready"] is True
    assert "VALIDATION_ERRORS" in summary["promotion_blockers"]


def test_dry_run_does_not_write(tmp_path):
    draft_path = tmp_path / "draft.json"
    output_path = tmp_path / "qa.json"
    write_json(draft_path, draft_with([valid_case()]))
    result = validate_draft(
        draft_path=draft_path,
        output_path=output_path,
        dry_run=True,
    )
    assert result["written"] is False
    assert not output_path.exists()


def test_write_mode_writes_qa_report(tmp_path):
    draft_path = tmp_path / "draft.json"
    output_path = tmp_path / "qa.json"
    write_json(draft_path, draft_with([valid_case()]))
    result = validate_draft(
        draft_path=draft_path,
        output_path=output_path,
        dry_run=False,
    )
    assert result["written"] is True
    assert output_path.exists()
    report = json.loads(output_path.read_text(encoding="utf-8"))
    assert report["promotion_allowed"] is False
    assert report["training_allowed"] is False


def test_promotion_blocked_if_errors_exist():
    case = valid_case()
    case["label_confidence"] = 1.5
    summary = evaluate_label_review_draft(
        draft=draft_with([case]),
        source_draft="draft.json",
    )
    assert summary["ready_for_promotion"] is False
    assert "VALIDATION_ERRORS" in summary["promotion_blockers"]
    assert "U04:INVALID_LABEL_CONFIDENCE" in summary["promotion_blockers"]


def test_invalid_training_approval_is_blocked():
    case = valid_case()
    case["approved_for_training"] = True
    summary = evaluate_label_review_draft(
        draft=draft_with([case]),
        source_draft="draft.json",
    )
    assert summary["errors_count"] > 0
    assert summary["ready_for_promotion"] is False
    assert "U04:INVALID_TRAINING_APPROVAL" in summary["promotion_blockers"]


def test_bridge_does_not_modify_draft(tmp_path):
    draft_path = tmp_path / "draft.json"
    output_path = tmp_path / "qa.json"
    write_json(draft_path, draft_with([valid_case()]))
    before = draft_path.read_bytes()
    validate_draft(
        draft_path=draft_path,
        output_path=output_path,
        dry_run=False,
    )
    assert draft_path.read_bytes() == before
