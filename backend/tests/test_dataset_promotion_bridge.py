import json
from pathlib import Path

import pytest

from app.ml.dataset_promotion_bridge import build_dataset_promotion_plan
from scripts.build_dataset_promotion_plan import build_plan


def write_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def approved_case(case_id="U04"):
    return {
        "case_id": case_id,
        "dataset_version": "shadow_review_draft",
        "review_status": "APPROVED",
        "previous_status": "UNDER_REVIEW",
        "reviewer": "reviewer-test",
        "review_time": "2026-06-29T00:00:00+00:00",
        "label_confidence": 0.9,
        "disagreement_reason": "Đã review disagreement.",
        "notes": "Label đã được xác nhận.",
        "approved_for_training": True,
        "anonymized": True,
        "source": "benchmark",
        "resolved_label": "weak",
        "stored_raw_text": False,
    }


def draft_with(cases, export_id="export-v1"):
    return {
        "export_id": export_id,
        "created_at": "2026-06-29T00:00:00+00:00",
        "source_queue": "queue.json",
        "status": "ready_for_label_review",
        "total_items": len(cases),
        "exported_items": [
            {"case_id": case["case_id"], "resolved_label": case["resolved_label"]}
            for case in cases
        ],
        "cases": cases,
        "approved_for_training": False,
        "stored_raw_text": False,
    }


def qa_report(source_draft, *, ready=1, errors=0, blockers=None):
    return {
        "status": "ready_for_promotion_planning" if ready else "ready_for_review",
        "source_draft": str(source_draft),
        "export_id": "export-v1",
        "total_cases": 1,
        "errors_count": errors,
        "warnings_count": 0,
        "ready_for_review": errors == 0,
        "ready_for_promotion_count": ready,
        "ready_for_promotion": ready > 0 and errors == 0,
        "not_ready": errors > 0,
        "promotion_blockers": blockers or [],
        "case_results": [],
        "promotion_allowed": False,
        "training_allowed": False,
    }


def manifest():
    return {"dataset_version": "dataset_v3", "total_cases": 310}


def test_no_report():
    from app.ml.dataset_promotion_bridge import build_no_qa_plan

    plan = build_no_qa_plan(source_qa_report="missing.json")
    assert plan["status"] == "no_qa_report"
    assert plan["promotion_allowed"] is False


def test_valid_qa_report_builds_plan():
    draft = draft_with([approved_case()])
    qa = qa_report("draft.json")
    plan = build_dataset_promotion_plan(
        qa_report=qa,
        draft=draft,
        manifest=manifest(),
        source_qa_report="qa.json",
        source_draft="draft.json",
    )
    assert plan["target_dataset_version"] == "dataset_v4"
    assert plan["promotion_ready"] == 1
    assert plan["estimated_dataset_size"] == 311


def test_blocked_promotion():
    case = approved_case()
    case["anonymized"] = False
    qa = qa_report("draft.json", ready=0, errors=1, blockers=["VALIDATION_ERRORS"])
    plan = build_dataset_promotion_plan(
        qa_report=qa,
        draft=draft_with([case]),
        manifest=manifest(),
        source_qa_report="qa.json",
        source_draft="draft.json",
    )
    assert plan["status"] == "blocked"
    assert plan["promotion_allowed"] is False
    assert plan["recommendation"] == "keep current dataset"


def test_promotion_allowed():
    plan = build_dataset_promotion_plan(
        qa_report=qa_report("draft.json"),
        draft=draft_with([approved_case()]),
        manifest=manifest(),
        source_qa_report="qa.json",
        source_draft="draft.json",
    )
    assert plan["status"] == "promotion_plan_ready"
    assert plan["promotion_allowed"] is True
    assert plan["promotion_executed"] is False
    assert plan["training_allowed"] is False


def test_duplicate_rejected():
    first = approved_case("U04")
    second = approved_case("U04")
    with pytest.raises(ValueError, match="duplicate case_id"):
        build_dataset_promotion_plan(
            qa_report=qa_report("draft.json", ready=2),
            draft=draft_with([first, second]),
            manifest=manifest(),
            source_qa_report="qa.json",
            source_draft="draft.json",
        )


def make_files(tmp_path):
    draft_path = tmp_path / "draft.json"
    qa_path = tmp_path / "qa.json"
    manifest_path = tmp_path / "manifest.json"
    output_path = tmp_path / "plan.json"
    write_json(draft_path, draft_with([approved_case()]))
    write_json(qa_path, qa_report(draft_path))
    write_json(manifest_path, manifest())
    return qa_path, draft_path, manifest_path, output_path


def test_dry_run(tmp_path):
    qa_path, _, manifest_path, output_path = make_files(tmp_path)
    result = build_plan(
        qa_path=qa_path,
        manifest_path=manifest_path,
        output_path=output_path,
        dry_run=True,
    )
    assert result["written"] is False
    assert not output_path.exists()


def test_write_mode(tmp_path):
    qa_path, _, manifest_path, output_path = make_files(tmp_path)
    result = build_plan(
        qa_path=qa_path,
        manifest_path=manifest_path,
        output_path=output_path,
        dry_run=False,
    )
    assert result["written"] is True
    assert output_path.exists()
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["promotion_executed"] is False
    assert payload["training_allowed"] is False


def test_inputs_not_modified(tmp_path):
    qa_path, draft_path, manifest_path, output_path = make_files(tmp_path)
    before = {
        qa_path: qa_path.read_bytes(),
        draft_path: draft_path.read_bytes(),
        manifest_path: manifest_path.read_bytes(),
    }
    build_plan(
        qa_path=qa_path,
        manifest_path=manifest_path,
        output_path=output_path,
        dry_run=False,
    )
    assert all(path.read_bytes() == content for path, content in before.items())
