import json
from datetime import datetime, timezone

from app.ai.dataset_export import (
    build_analysis_summary,
    build_benchmark_case,
    build_dataset_payload,
    build_feedback_label,
    write_dataset_json,
)
from app.models.match_analysis import MatchAnalysis
from app.models.user_feedback import UserFeedback


def test_build_analysis_summary_excludes_text_and_pii():
    analysis = MatchAnalysis(
        id=10,
        user_id=2,
        resume_id=3,
        job_description_id=4,
        match_score=72.5,
        matched_skills=json.dumps(["Python", "REST API"]),
        missing_skills=json.dumps(["Docker"]),
        keyword_overlap=json.dumps(["api"]),
        summary="Không export field này trong dataset summary.",
        suggestions="[]",
        created_at=datetime(2026, 6, 21, tzinfo=timezone.utc),
    )

    summary = build_analysis_summary(analysis)

    assert summary["analysis_id"] == 10
    assert summary["actual_score"] == 72.5
    assert summary["matched_skills"] == ["Python", "REST API"]
    assert summary["missing_skills"] == ["Docker"]
    assert "summary" not in summary
    assert "resume_text" not in summary
    assert "email" not in summary


def test_build_feedback_label_maps_useful_to_agreement():
    feedback = UserFeedback(
        id=5,
        user_id=2,
        feedback_type="analysis",
        useful=False,
        comment="Điểm hơi cao so với cảm nhận của user.",
        created_at=datetime(2026, 6, 21, tzinfo=timezone.utc),
    )

    label = build_feedback_label(
        feedback,
        case_id="U011",
        expected_score_range="35-50",
        disagreement_notes="User thấy role mismatch bị đánh giá cao.",
    )

    assert label["case_id"] == "U011"
    assert label["user_agreed"] is False
    assert label["user_disagreed"] is True
    assert label["expected_score_range"] == "35-50"


def test_build_dataset_payload_and_write_json(tmp_path):
    case = build_benchmark_case(
        case_id="U011",
        role_family="backend",
        candidate_stack="Node.js",
        target_role="Backend .NET Intern",
        expected_fit="same_role_different_stack",
        actual_score=61.2,
        confidence="medium",
        review_notes="Case mẫu đã ẩn danh.",
    )
    payload = build_dataset_payload(dataset_name="beta-evaluation-v1", benchmark_cases=[case])
    output_path = tmp_path / "dataset.json"

    write_dataset_json(payload, output_path)

    loaded = json.loads(output_path.read_text(encoding="utf-8"))
    assert loaded["schema_version"] == "careeros-dataset-v1"
    assert loaded["dataset_name"] == "beta-evaluation-v1"
    assert loaded["benchmark_cases"][0]["case_id"] == "U011"
