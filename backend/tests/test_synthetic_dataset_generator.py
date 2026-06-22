from collections import Counter

from scripts.generate_synthetic_dataset import CATEGORIES, SENIORITIES, ROLE_TEMPLATES, generate_cases


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
    "seniority",
    "category",
}


def test_generate_synthetic_dataset_has_expected_size_and_categories():
    cases = generate_cases()

    assert len(cases) == 300
    assert Counter(case["category"] for case in cases) == {category: 30 for category in CATEGORIES}
    assert cases[0]["case_id"] == "SYN001"
    assert cases[-1]["case_id"] == "SYN300"


def test_generate_synthetic_dataset_has_required_fields_labels_roles_and_seniority():
    cases = generate_cases()
    labels = {case["fit_label"] for case in cases}
    roles = {case["target_role"] for case in cases}
    expected_roles = {role["target_role"] for role in ROLE_TEMPLATES}
    seniorities = {case["seniority"] for case in cases}

    assert labels == {"good", "medium", "weak", "mismatch"}
    assert roles == expected_roles
    assert seniorities == set(SENIORITIES)
    for case in cases:
        assert REQUIRED_FIELDS.issubset(case)
        assert case["dataset_type"] == "synthetic"
        assert case["skill_overlap"] is not None
        assert case["missing_critical_skills"] is not None