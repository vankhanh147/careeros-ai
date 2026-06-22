"""Feature extraction for the trainable matching prototype.

This module intentionally builds simple text features for TF-IDF. It does not
touch production scoring and does not depend on user data.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


FEATURE_FIELDS = (
    "resume_summary",
    "job_description_summary",
    "target_role",
    "role_family",
    "candidate_stack",
    "jd_stack",
    "missing_critical_skills",
    "skill_overlap",
)


def build_matching_feature_text(case: Mapping[str, Any]) -> str:
    """Convert a synthetic/runtime matching payload into one TF-IDF text row."""

    parts: list[str] = []
    for field in FEATURE_FIELDS:
        text = _stringify_feature(case.get(field))
        if text:
            parts.append(f"{field}: {text}")
    return "\n".join(parts).strip()


def build_feature_corpus(cases: Sequence[Mapping[str, Any]]) -> list[str]:
    return [build_matching_feature_text(case) for case in cases]


def _stringify_feature(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return ", ".join(str(item).strip() for item in value if str(item).strip())
    return str(value).strip()

