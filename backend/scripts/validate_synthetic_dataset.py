import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = ROOT / "docs" / "datasets" / "synthetic" / "synthetic_cases.json"

EXPECTED_CASE_COUNT = 70
EXPECTED_GROUPS = {
    "exact_fit",
    "same_role_different_stack",
    "role_mismatch",
    "cross_domain_transferable",
    "weak_cv",
    "keyword_stuffing",
    "non_it_mismatch",
}
VALID_FIT_LABELS = {"good", "medium", "weak", "mismatch"}
VALID_ROLE_FAMILIES = {"backend", "frontend", "fullstack", "mobile", "ai/data", "devops", "qa/testing", "cybersecurity", "general software"}
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
MOJIBAKE_PATTERN = re.compile(
    "\u00c3|\u00c4|\u00e1\u00ba|\u00e1\u00bb|\u00c6|\u00c5|\u00c2|\ufffd|M\\?|Kh\\?|H\\?\\?|tr\\?|\\?\\?\\?"
)
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_PATTERN = re.compile(r"(?<!\d)(?:\+?\d[\s.-]?){9,14}(?!\d)")
RAW_SOURCE_PATTERN = re.compile(r"(linkedin\.com|indeed\.com|topcv\.vn|vietnamworks\.com|phone:|email:)", re.IGNORECASE)


def load_dataset(path: Path = DATASET_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_dataset(payload: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    cases = payload.get("cases")

    if not isinstance(cases, list):
        return {"errors": ["Dataset field 'cases' phải là list."], "warnings": [], "summary": {}}

    if payload.get("dataset_type") != "synthetic":
        errors.append("dataset_type phải là synthetic.")
    if payload.get("case_count") != EXPECTED_CASE_COUNT:
        errors.append(f"case_count phải là {EXPECTED_CASE_COUNT}.")
    if len(cases) != EXPECTED_CASE_COUNT:
        errors.append(f"Số lượng cases phải là {EXPECTED_CASE_COUNT}, hiện có {len(cases)}.")

    case_ids = [str(case.get("case_id", "")) for case in cases if isinstance(case, dict)]
    duplicate_ids = sorted([case_id for case_id, count in Counter(case_ids).items() if count > 1])
    if duplicate_ids:
        errors.append(f"case_id bị trùng: {', '.join(duplicate_ids)}.")

    group_counts = Counter(str(case.get("group", "")) for case in cases if isinstance(case, dict))
    if set(group_counts) != EXPECTED_GROUPS:
        errors.append(f"Nhóm case không khớp expected groups: {sorted(group_counts)}.")
    for group in EXPECTED_GROUPS:
        if group_counts.get(group, 0) != 10:
            errors.append(f"Nhóm {group} phải có 10 case, hiện có {group_counts.get(group, 0)}.")

    label_counts: Counter[str] = Counter()
    range_widths: dict[str, list[int]] = {}

    for index, case in enumerate(cases, start=1):
        if not isinstance(case, dict):
            errors.append(f"Case #{index} không phải object.")
            continue
        case_id = str(case.get("case_id") or f"case #{index}")
        missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in case)
        if missing_fields:
            errors.append(f"{case_id} thiếu field: {', '.join(missing_fields)}.")

        fit_label = str(case.get("fit_label", ""))
        label_counts[fit_label] += 1
        if fit_label not in VALID_FIT_LABELS:
            errors.append(f"{case_id} có fit_label không hợp lệ: {fit_label}.")

        role_family = str(case.get("role_family", ""))
        if role_family not in VALID_ROLE_FAMILIES:
            errors.append(f"{case_id} có role_family không hợp lệ: {role_family}.")

        score_range = str(case.get("expected_score_range", ""))
        parsed_range = _parse_score_range(score_range)
        if parsed_range is None:
            errors.append(f"{case_id} có expected_score_range không hợp lệ: {score_range}.")
        else:
            low, high = parsed_range
            width = high - low
            range_widths.setdefault(score_range, []).append(width)
            if width < 10:
                warnings.append(f"{case_id} có expected_score_range khá hẹp: {score_range}.")
            if width > 30:
                warnings.append(f"{case_id} có expected_score_range khá rộng: {score_range}.")

        reason = str(case.get("reason") or "").strip()
        if not reason:
            errors.append(f"{case_id} thiếu reason.")
        if len(reason) < 40:
            warnings.append(f"{case_id} có reason hơi ngắn, nên review lại.")

        missing_critical = case.get("missing_critical_skills")
        if not isinstance(missing_critical, list):
            errors.append(f"{case_id} missing_critical_skills phải là list.")
        elif fit_label == "mismatch" and not missing_critical:
            errors.append(f"{case_id} là mismatch nhưng missing_critical_skills rỗng.")

        skill_overlap = case.get("skill_overlap")
        if not isinstance(skill_overlap, list):
            errors.append(f"{case_id} skill_overlap phải là list.")

        text_blob = json.dumps(case, ensure_ascii=False)
        if MOJIBAKE_PATTERN.search(text_blob):
            errors.append(f"{case_id} có dấu hiệu mojibake.")
        if EMAIL_PATTERN.search(text_blob):
            errors.append(f"{case_id} có dấu hiệu email/PII.")
        if PHONE_PATTERN.search(text_blob):
            errors.append(f"{case_id} có dấu hiệu số điện thoại/PII.")
        if RAW_SOURCE_PATTERN.search(text_blob):
            errors.append(f"{case_id} có dấu hiệu source thật hoặc raw JD/CV.")

        if case.get("group") == "keyword_stuffing" and len(case.get("skill_overlap") or []) > 3:
            warnings.append(f"{case_id} keyword_stuffing có quá nhiều overlap, dễ gây nhiễu.")
        if case.get("group") == "exact_fit" and fit_label != "good":
            errors.append(f"{case_id} thuộc exact_fit nhưng fit_label không phải good.")
        if case.get("group") == "non_it_mismatch" and fit_label != "mismatch":
            errors.append(f"{case_id} thuộc non_it_mismatch nhưng fit_label không phải mismatch.")

    return {
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "case_count": len(cases),
            "group_counts": dict(sorted(group_counts.items())),
            "label_counts": dict(sorted(label_counts.items())),
            "expected_score_ranges": sorted(range_widths),
        },
    }


def _parse_score_range(value: str) -> tuple[int, int] | None:
    match = re.fullmatch(r"\s*(\d{1,3})\s*-\s*(\d{1,3})\s*", value)
    if not match:
        return None
    low = int(match.group(1))
    high = int(match.group(2))
    if low < 0 or high > 100 or low >= high:
        return None
    return low, high


def main() -> int:
    payload = load_dataset()
    result = validate_dataset(payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
