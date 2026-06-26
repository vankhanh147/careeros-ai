"""Assemble the CareerOS AI training dataset artifact.

Script này chỉ tạo artifact dataset offline cho training/evaluation sau này.
Nó không train model, không thay production scoring và không tích hợp runtime.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.ml.training_infra import load_label_review_cases, validate_label_review_case


VALID_LABELS = {"good", "medium", "weak", "mismatch"}
VALID_SOURCES = {"synthetic", "benchmark", "beta"}
DEFAULT_DATASET_VERSION = "dataset_v3"
SYNTHETIC_PATH = ROOT_DIR / "docs" / "datasets" / "synthetic" / "synthetic_cases.json"
BENCHMARK_PATH = ROOT_DIR / "docs" / "benchmark-v1" / "benchmark_cases.md"
DEFAULT_BETA_REVIEWS_PATH = BACKEND_DIR / "ml" / "reviews" / "sample_review_cases.json"
DATASETS_DIR = BACKEND_DIR / "ml" / "datasets"
REPORTS_DIR = BACKEND_DIR / "ml" / "reports"
ARTIFACT_PATH = DATASETS_DIR / "training_dataset_v3.json"
MANIFEST_PATH = DATASETS_DIR / "training_dataset_manifest.json"
STATISTICS_PATH = REPORTS_DIR / "training_dataset_statistics.json"

MOJIBAKE_PATTERN = re.compile(r"\u00c3|\u00c2|\u00e1\u00ba|\u00e1\u00bb|\u00c4|\u00c6|\u00c5|\ufffd|M\?|Kh\?|H\?\?|tr\?|\?\?\?")
EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_PATTERN = re.compile(r"(?<!\d)(?:\+?\d[\d\s().-]{8,}\d)(?!\d)")
ISO_TIMESTAMP_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z?")

BENCHMARK_LABELS = {
    "U01": "good",
    "U02": "medium",
    "U03": "good",
    "U04": "weak",
    "U05": "medium",
    "U06": "weak",
    "U07": "weak",
    "U08": "weak",
    "U09": "weak",
    "U10": "mismatch",
}

BENCHMARK_ROLE_FAMILIES = {
    "U01": "backend",
    "U02": "backend",
    "U03": "frontend",
    "U04": "backend",
    "U05": "backend",
    "U06": "frontend",
    "U07": "ai/data",
    "U08": "backend",
    "U09": "frontend",
    "U10": "backend",
}

BENCHMARK_CATEGORIES = {
    "U01": "exact_fit",
    "U02": "same_role_different_stack",
    "U03": "exact_fit",
    "U04": "role_mismatch",
    "U05": "cross_domain_transferable",
    "U06": "role_mismatch",
    "U07": "cross_domain_transferable",
    "U08": "cross_domain_transferable",
    "U09": "role_mismatch",
    "U10": "non_it_mismatch",
}




def serialized_for_safety_scan(case: dict[str, Any]) -> str:
    safe_case = {key: value for key, value in case.items() if key != "content_hash"}
    return json.dumps(safe_case, ensure_ascii=False)


def has_pii_signal(serialized: str) -> bool:
    pii_scan_text = ISO_TIMESTAMP_PATTERN.sub("", serialized)
    return bool(EMAIL_PATTERN.search(serialized) or PHONE_PATTERN.search(pii_scan_text))
def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def stable_json(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def content_hash_for_case(case: dict[str, Any]) -> str:
    text = "\n".join(
        [
            str(case.get("resume_summary") or ""),
            str(case.get("job_description_summary") or ""),
            str(case.get("target_role") or ""),
        ]
    ).strip().lower()
    return sha256_text(text)


def normalize_training_case(case: dict[str, Any], *, source: str) -> dict[str, Any]:
    label = str(case.get("fit_label") or case.get("expected_label") or "").strip()
    normalized = {
        "case_id": str(case.get("case_id") or "").strip(),
        "source": source,
        "source_category": str(case.get("category") or case.get("group") or source).strip(),
        "seniority": str(case.get("seniority") or "unknown").strip(),
        "candidate_profile": str(case.get("candidate_profile") or "").strip(),
        "resume_summary": str(case.get("resume_summary") or case.get("candidate_profile") or "").strip(),
        "job_description_summary": str(case.get("job_description_summary") or case.get("jd_summary") or case.get("target_role") or "").strip(),
        "target_role": str(case.get("target_role") or "unknown").strip(),
        "role_family": str(case.get("role_family") or "general software").strip(),
        "candidate_stack": str(case.get("candidate_stack") or "unknown").strip(),
        "jd_stack": str(case.get("jd_stack") or "unknown").strip(),
        "fit_label": label,
        "expected_score_range": str(case.get("expected_score_range") or "").strip(),
        "reason": str(case.get("reason") or case.get("review_notes") or "").strip(),
        "skill_overlap": list(case.get("skill_overlap") or []),
        "missing_critical_skills": list(case.get("missing_critical_skills") or []),
        "review_status": str(case.get("review_status") or "not_required").strip(),
        "approved_for_training": bool(case.get("approved_for_training", source != "beta")),
        "anonymized": bool(case.get("anonymized", source != "beta")),
    }
    normalized["content_hash"] = content_hash_for_case(normalized)
    return normalized


def load_synthetic_cases(path: Path = SYNTHETIC_PATH) -> list[dict[str, Any]]:
    payload = load_json(path)
    cases = payload.get("cases", []) if isinstance(payload, dict) else payload
    if not isinstance(cases, list):
        raise ValueError("Synthetic dataset field cases phải là list.")
    return [normalize_training_case(dict(case), source="synthetic") for case in cases if isinstance(case, dict)]


def load_benchmark_cases(path: Path = BENCHMARK_PATH) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("| U"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) < 8:
            continue
        case_id, cv_persona, jd_target, expected_behavior, _v1, v2_score, note, purpose = cells[:8]
        case = {
            "case_id": case_id,
            "category": BENCHMARK_CATEGORIES.get(case_id, "benchmark"),
            "seniority": "unknown",
            "candidate_profile": cv_persona,
            "resume_summary": f"Benchmark CV persona: {cv_persona}. Purpose: {purpose}.",
            "job_description_summary": f"Benchmark JD target: {jd_target}. Expected behavior: {expected_behavior}.",
            "target_role": jd_target,
            "role_family": BENCHMARK_ROLE_FAMILIES.get(case_id, "general software"),
            "candidate_stack": cv_persona,
            "jd_stack": jd_target,
            "fit_label": BENCHMARK_LABELS.get(case_id, label_from_score(v2_score)),
            "expected_score_range": score_range_from_label(BENCHMARK_LABELS.get(case_id, label_from_score(v2_score))),
            "reason": note or expected_behavior,
            "skill_overlap": [],
            "missing_critical_skills": [],
        }
        rows.append(normalize_training_case(case, source="benchmark"))
    return rows


def label_from_score(value: str) -> str:
    try:
        score = float(str(value).strip())
    except ValueError:
        return "weak"
    if score >= 75:
        return "good"
    if score >= 50:
        return "medium"
    if score >= 25:
        return "weak"
    return "mismatch"


def score_range_from_label(label: str) -> str:
    return {
        "good": "75-90",
        "medium": "50-70",
        "weak": "25-50",
        "mismatch": "10-35",
    }.get(label, "25-50")


def load_approved_beta_cases(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for case in load_label_review_cases(path):
        errors = validate_label_review_case(case)
        if errors:
            rows.append({"__invalid__": True, "case_id": case.get("case_id"), "errors": errors})
            continue
        if not case.get("approved_for_training"):
            rows.append({"__invalid__": True, "case_id": case.get("case_id"), "errors": ["Beta case chưa approved_for_training."]})
            continue
        rows.append(normalize_training_case(case, source="beta"))
    return rows


def validate_training_cases(cases: list[dict[str, Any]]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    case_ids: Counter[str] = Counter()
    content_hashes: Counter[str] = Counter()

    for index, case in enumerate(cases, start=1):
        if case.get("__invalid__"):
            case_id = case.get("case_id") or f"case_{index}"
            for error in case.get("errors", []):
                errors.append(f"{case_id}: {error}")
            continue

        case_id = str(case.get("case_id") or "").strip()
        source = str(case.get("source") or "").strip()
        label = str(case.get("fit_label") or "").strip()
        content_hash = str(case.get("content_hash") or "").strip()
        serialized = serialized_for_safety_scan(case)

        if not case_id:
            errors.append(f"Case #{index} thiếu case_id.")
        else:
            case_ids[case_id] += 1
        if not content_hash:
            errors.append(f"{case_id or index}: thiếu content_hash.")
        else:
            content_hashes[content_hash] += 1
        if source not in VALID_SOURCES:
            errors.append(f"{case_id}: source không hợp lệ: {source}.")
        if not label:
            errors.append(f"{case_id}: thiếu label.")
        elif label not in VALID_LABELS:
            errors.append(f"{case_id}: label không hợp lệ: {label}.")
        if not str(case.get("resume_summary") or "").strip():
            errors.append(f"{case_id}: thiếu resume_summary.")
        if not str(case.get("job_description_summary") or "").strip():
            errors.append(f"{case_id}: thiếu job_description_summary.")
        if source == "beta":
            if case.get("review_status") not in {"APPROVED", "PROMOTED", "TRAINABLE"}:
                errors.append(f"{case_id}: beta review chưa approved.")
            if case.get("approved_for_training") is not True:
                errors.append(f"{case_id}: beta chưa approved_for_training.")
            if case.get("anonymized") is not True:
                errors.append(f"{case_id}: beta chưa anonymized.")
        if MOJIBAKE_PATTERN.search(serialized):
            errors.append(f"{case_id}: có dấu hiệu mojibake.")
        pii_scan_text = ISO_TIMESTAMP_PATTERN.sub("", serialized)
        if EMAIL_PATTERN.search(serialized) or PHONE_PATTERN.search(pii_scan_text):
            errors.append(f"{case_id}: có dấu hiệu PII.")

    duplicate_ids = sorted(case_id for case_id, count in case_ids.items() if count > 1)
    duplicate_hashes = sorted(value for value, count in content_hashes.items() if count > 1)
    if duplicate_ids:
        errors.append(f"case_id bị trùng: {', '.join(duplicate_ids)}.")
    if duplicate_hashes:
        errors.append(f"content hash bị trùng: {', '.join(duplicate_hashes[:5])}.")

    return {"errors": errors, "warnings": warnings}


def build_training_dataset(
    *,
    dataset_version: str = DEFAULT_DATASET_VERSION,
    synthetic_path: Path = SYNTHETIC_PATH,
    benchmark_path: Path = BENCHMARK_PATH,
    beta_reviews_path: Path | None = None,
) -> dict[str, Any]:
    synthetic_cases = load_synthetic_cases(synthetic_path)
    benchmark_cases = load_benchmark_cases(benchmark_path)
    beta_cases = load_approved_beta_cases(beta_reviews_path) if beta_reviews_path else []
    cases = synthetic_cases + benchmark_cases + beta_cases
    validation = validate_training_cases(cases)
    payload = {
        "schema_version": "careeros-training-dataset-v1",
        "dataset_version": dataset_version,
        "case_count": len(cases),
        "sources": {
            "synthetic": len(synthetic_cases),
            "benchmark": len(benchmark_cases),
            "beta": len(beta_cases),
        },
        "cases": cases,
    }
    return {"payload": payload, "validation": validation}


def build_statistics(payload: dict[str, Any]) -> dict[str, Any]:
    cases = payload.get("cases", [])
    source_counts = Counter(str(case.get("source") or "unknown") for case in cases)
    beta_cases = [case for case in cases if case.get("source") == "beta"]
    approved_beta = [case for case in beta_cases if case.get("approved_for_training") is True]
    return {
        "dataset_version": payload.get("dataset_version"),
        "total_cases": len(cases),
        "role_distribution": dict(sorted(Counter(str(case.get("role_family") or "unknown") for case in cases).items())),
        "category_distribution": dict(sorted(Counter(str(case.get("source_category") or "unknown") for case in cases).items())),
        "label_distribution": dict(sorted(Counter(str(case.get("fit_label") or "unknown") for case in cases).items())),
        "seniority_distribution": dict(sorted(Counter(str(case.get("seniority") or "unknown") for case in cases).items())),
        "source_distribution": dict(sorted(source_counts.items())),
        "approved_beta_percent": round((len(approved_beta) / len(beta_cases)) * 100, 2) if beta_cases else 0.0,
    }




def display_path(path: Path, base: Path = BACKEND_DIR) -> str:
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)
def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def export_training_dataset(
    *,
    payload: dict[str, Any],
    artifact_path: Path = ARTIFACT_PATH,
    manifest_path: Path = MANIFEST_PATH,
    statistics_path: Path = STATISTICS_PATH,
    source_files: dict[str, str] | None = None,
) -> dict[str, Any]:
    write_json(artifact_path, payload)
    artifact_hash = sha256_text(stable_json(payload))
    statistics = build_statistics(payload)
    write_json(statistics_path, statistics)
    manifest = {
        "dataset_version": payload["dataset_version"],
        "synthetic_count": payload["sources"]["synthetic"],
        "benchmark_count": payload["sources"]["benchmark"],
        "beta_count": payload["sources"]["beta"],
        "total_cases": payload["case_count"],
        "source_files": source_files or {},
        "artifact_name": artifact_path.name,
        "artifact_hash": artifact_hash,
        "statistics_file": display_path(statistics_path),
        "notes": "Training dataset artifact v3 được assembly offline; không thay production scoring.",
    }
    write_json(manifest_path, manifest)
    return {"manifest": manifest, "statistics": statistics}


def run_assembly(
    *,
    dataset_version: str,
    beta_reviews_path: Path | None,
    dry_run: bool,
    artifact_path: Path = ARTIFACT_PATH,
    manifest_path: Path = MANIFEST_PATH,
    statistics_path: Path = STATISTICS_PATH,
) -> dict[str, Any]:
    result = build_training_dataset(dataset_version=dataset_version, beta_reviews_path=beta_reviews_path)
    validation = result["validation"]
    if validation["errors"]:
        return {"ok": False, "validation": validation, "payload": result["payload"]}
    if dry_run:
        return {"ok": True, "dry_run": True, "validation": validation, "payload": result["payload"]}
    exported = export_training_dataset(
        payload=result["payload"],
        artifact_path=artifact_path,
        manifest_path=manifest_path,
        statistics_path=statistics_path,
        source_files={
            "synthetic": str(SYNTHETIC_PATH.relative_to(ROOT_DIR)),
            "benchmark": str(BENCHMARK_PATH.relative_to(ROOT_DIR)),
            "beta_reviews": str(beta_reviews_path.relative_to(ROOT_DIR)) if beta_reviews_path else "",
        },
    )
    return {"ok": True, "dry_run": False, "validation": validation, "payload": result["payload"], **exported}


def print_summary(result: dict[str, Any]) -> None:
    payload = result["payload"]
    validation = result["validation"]
    print("CareerOS Training Dataset Assembly")
    print("=" * 40)
    print(f"Dataset version: {payload['dataset_version']}")
    print(f"Total cases: {payload['case_count']}")
    print(f"Synthetic: {payload['sources']['synthetic']}")
    print(f"Benchmark: {payload['sources']['benchmark']}")
    print(f"Beta: {payload['sources']['beta']}")
    print(f"Errors: {len(validation['errors'])}")
    print(f"Warnings: {len(validation['warnings'])}")
    if validation["errors"]:
        print("Errors:")
        for error in validation["errors"]:
            print(f"  - {error}")
    if result.get("dry_run"):
        print("Dry-run: không ghi artifact, manifest hoặc statistics.")
    elif result.get("ok"):
        manifest = result.get("manifest", {})
        print(f"Artifact: {ARTIFACT_PATH}")
        print(f"Manifest: {MANIFEST_PATH}")
        print(f"Statistics: {STATISTICS_PATH}")
        print(f"Artifact hash: {manifest.get('artifact_hash')}")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Build training dataset artifact cho CareerOS AI.")
    parser.add_argument("--dataset-version", default=DEFAULT_DATASET_VERSION, help="Dataset version cần assembly.")
    parser.add_argument("--beta-reviews", default="", help="File review labels đã approved để thêm vào dataset.")
    parser.add_argument("--dry-run", action="store_true", help="Chỉ validate/in kế hoạch, không ghi file.")
    args = parser.parse_args()

    beta_path = Path(args.beta_reviews) if args.beta_reviews else None
    result = run_assembly(dataset_version=args.dataset_version, beta_reviews_path=beta_path, dry_run=args.dry_run)
    print_summary(result)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())