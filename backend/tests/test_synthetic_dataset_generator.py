from collections import Counter

from scripts.generate_synthetic_dataset import GROUPS, generate_cases


REQUIRED_FIELDS = {
    "case_id",
    "candidate_profile",
    "resume_summary",
    "job_description_summary",
    "target_role",
    "role_family",
    "candidate_stack",
    "jd_stack",
    "fit_label",
    "expected_score_range",
    "reason",
    "skill_overlap",
    "missing_critical_skills",
}


def test_generate_synthetic_dataset_has_expected_size_and_groups():
    cases = generate_cases()

    assert len(cases) == 70
    assert Counter(case["group"] for case in cases) == {group: 10 for group in GROUPS}
    assert cases[0]["case_id"] == "SYN001"
    assert cases[-1]["case_id"] == "SYN070"


def test_generate_synthetic_dataset_has_required_fields_and_labels():
    cases = generate_cases()
    labels = {case["fit_label"] for case in cases}

    assert labels == {"good", "medium", "weak", "mismatch"}
    for case in cases:
        assert REQUIRED_FIELDS.issubset(case)
        assert case["dataset_type"] == "synthetic"
        assert case["skill_overlap"] is not None
        assert case["missing_critical_skills"] is not None
