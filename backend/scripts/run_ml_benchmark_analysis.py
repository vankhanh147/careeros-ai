"""Run Phase 9.1 ML benchmark and disagreement analysis.

This script uses existing model artifacts from Phase 9.0. It does not train a
new model and does not change production scoring.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import json
import sys
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.ml.features import build_matching_feature_text
from app.ml.matching_predictor import predict_matching_fit
from app.ml.train_matching_model import split_matching_cases
from app.services.resume_job_matcher import analyze_resume_job_match


DATASET_PATH = ROOT_DIR / "docs" / "datasets" / "synthetic" / "synthetic_cases.json"
REPORT_PATH = ROOT_DIR / "context" / "PHASE_9_1_ML_BENCHMARK_REPORT.md"
ERROR_REPORT_PATH = ROOT_DIR / "docs" / "datasets" / "synthetic" / "ml_error_analysis_v1.md"


BENCHMARK_CASES: list[dict[str, Any]] = [
    {
        "case_id": "U01",
        "scenario": ".NET Backend Intern -> .NET Backend JD",
        "expected_score_range": "75-90",
        "expected_label": "good",
        "resume_text": "Backend intern resume. Projects: built a task management backend API using C#, .NET, ASP.NET Core and PostgreSQL. Implemented REST API CRUD endpoints, JWT authentication, validation, SQL queries, Git/GitHub workflow and Docker deployment basics.",
        "jd_text": "Backend JD requiring C# .NET ASP.NET Core REST API JWT authentication PostgreSQL SQL Docker and testing.",
    },
    {
        "case_id": "U02",
        "scenario": "Node.js Backend -> .NET Backend JD",
        "expected_score_range": "50-70",
        "expected_label": "medium",
        "resume_text": "Backend developer resume. Projects: built e-commerce REST API using Node.js, Express, JavaScript and MongoDB. Implemented JWT authentication, database models, Git/GitHub and Docker. No C#, .NET or ASP.NET Core project.",
        "jd_text": "Backend JD requiring C# .NET ASP.NET Core REST API JWT authentication PostgreSQL SQL Docker and testing.",
    },
    {
        "case_id": "U03",
        "scenario": "React Frontend -> React Frontend JD",
        "expected_score_range": "80-90",
        "expected_label": "good",
        "resume_text": "Frontend developer resume. Projects: built React and Next.js UI with TypeScript, JavaScript, HTML, CSS and Tailwind. Integrated REST API, handled authentication state, forms, loading, empty and error states.",
        "jd_text": "Frontend JD requiring React Next.js TypeScript JavaScript HTML CSS Tailwind REST API integration authentication and production-ready UI states.",
    },
    {
        "case_id": "U04",
        "scenario": "React Frontend -> .NET Backend JD",
        "expected_score_range": "25-50",
        "expected_label": "weak",
        "resume_text": "Frontend developer resume. Projects: built React and Next.js UI with TypeScript, JavaScript, HTML, CSS and Tailwind. Integrated REST API from backend services. No backend project with C#, .NET, ASP.NET Core or database schema.",
        "jd_text": "Backend JD requiring C# .NET ASP.NET Core REST API JWT authentication PostgreSQL SQL Docker and testing.",
    },
    {
        "case_id": "U05",
        "scenario": "AI/Python Backend -> .NET Backend JD",
        "expected_score_range": "35-60",
        "expected_label": "medium",
        "resume_text": "AI and Python backend resume. Projects: built Python FastAPI service, REST API, PostgreSQL database, machine learning experiments, pandas, scikit-learn and authentication basics. No C#, .NET or ASP.NET Core production project.",
        "jd_text": "Backend JD requiring C# .NET ASP.NET Core REST API JWT authentication PostgreSQL SQL Docker and testing.",
    },
    {
        "case_id": "U06",
        "scenario": ".NET Backend -> React Frontend JD",
        "expected_score_range": "25-50",
        "expected_label": "weak",
        "resume_text": "Backend intern resume. Projects: built ASP.NET Core REST API with C#, .NET, PostgreSQL, JWT authentication, validation, SQL queries and Docker deployment. No React, Next.js, TypeScript frontend UI project.",
        "jd_text": "Frontend JD requiring React Next.js TypeScript JavaScript HTML CSS Tailwind REST API integration authentication and production-ready UI states.",
    },
    {
        "case_id": "U07",
        "scenario": "Flutter Mobile -> AI/ML JD",
        "expected_score_range": "35-60",
        "expected_label": "weak",
        "resume_text": "Mobile developer resume. Projects: built Flutter mobile app with Firebase authentication, REST API integration and some Python scripting for automation. No machine learning, NLP, pandas, numpy or scikit-learn project.",
        "jd_text": "AI intern role requiring Python machine learning NLP pandas numpy scikit-learn PyTorch TensorFlow sentence transformers and model evaluation.",
    },
    {
        "case_id": "U08",
        "scenario": "Data Analyst -> .NET Backend JD",
        "expected_score_range": "35-60",
        "expected_label": "weak",
        "resume_text": "Data analyst resume. Projects: SQL dashboards, Python pandas data cleaning, Excel reporting, business analysis and data visualization. No backend API implementation, no C#, no ASP.NET Core and no JWT authentication project.",
        "jd_text": "Backend JD requiring C# .NET ASP.NET Core REST API JWT authentication PostgreSQL SQL Docker and testing.",
    },
    {
        "case_id": "U09",
        "scenario": "Cybersecurity -> React Frontend JD",
        "expected_score_range": "25-50",
        "expected_label": "weak",
        "resume_text": "Cybersecurity resume. Projects: web security testing, authentication review, vulnerability assessment, Linux basics and JavaScript security notes. No React, Next.js, TypeScript or production frontend UI project.",
        "jd_text": "Frontend JD requiring React Next.js TypeScript JavaScript HTML CSS Tailwind REST API integration authentication and production-ready UI states.",
    },
    {
        "case_id": "U10",
        "scenario": "Marketing/Business -> .NET Backend JD",
        "expected_score_range": "10-35",
        "expected_label": "mismatch",
        "resume_text": "Marketing and business resume. Experience: campaign planning, user research and content strategy. No software engineering project, no backend, no API implementation, no C#, no .NET and no authentication experience.",
        "jd_text": "Backend JD requiring C# .NET ASP.NET Core REST API JWT authentication PostgreSQL SQL Docker and testing.",
    },
]


LABEL_RANK = {"mismatch": 0, "weak": 1, "medium": 2, "good": 3}


def main() -> None:
    benchmark_rows = run_benchmark_cases()
    synthetic_analysis = analyze_synthetic_test_errors()
    REPORT_PATH.write_text(build_phase_report(benchmark_rows, synthetic_analysis), encoding="utf-8")
    ERROR_REPORT_PATH.write_text(build_synthetic_error_report(synthetic_analysis), encoding="utf-8")

    print("CareerOS Phase 9.1 ML benchmark analysis")
    print("=" * 48)
    for row in benchmark_rows:
        print(
            f"{row['case_id']} | score={row['rule_based_score']} | "
            f"hybrid={row['hybrid_score_candidate']} | "
            f"ML={row['ml_predicted_label']} ({row['ml_confidence']}) | "
            f"{row['agreement_status']}"
        )
    print()
    print(f"Report: {REPORT_PATH}")
    print(f"Synthetic error report: {ERROR_REPORT_PATH}")


def run_benchmark_cases() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for case in BENCHMARK_CASES:
        result = analyze_resume_job_match(case["resume_text"], case["jd_text"])
        ml = result.get("ml_evaluation", {})
        row = {
            "case_id": case["case_id"],
            "scenario": case["scenario"],
            "expected_score_range": case["expected_score_range"],
            "expected_label": case["expected_label"],
            "rule_based_score": result["match_score"],
            "hybrid_score_candidate": result.get("hybrid_evaluation", {}).get("hybrid_score_candidate"),
            "ml_predicted_label": ml.get("predicted_label") or "unavailable",
            "ml_confidence": ml.get("confidence"),
            "ml_probabilities": ml.get("label_probabilities") or {},
            "agreement_status": classify_agreement(
                rule_score=float(result["match_score"]),
                expected_label=case["expected_label"],
                ml_label=str(ml.get("predicted_label") or "unavailable"),
                ml_confidence=ml.get("confidence"),
            ),
        }
        rows.append(row)
    return rows


def classify_agreement(*, rule_score: float, expected_label: str, ml_label: str, ml_confidence: float | None) -> str:
    if ml_label == "unavailable":
        return "needs_review"
    if ml_confidence is None or ml_confidence < 0.45:
        return "needs_review"
    score_label = label_from_score(rule_score)
    if ml_label == expected_label and ml_label == score_label:
        return "aligned"
    distance_to_expected = abs(LABEL_RANK.get(ml_label, -1) - LABEL_RANK.get(expected_label, -1))
    distance_to_score = abs(LABEL_RANK.get(ml_label, -1) - LABEL_RANK.get(score_label, -1))
    if distance_to_expected >= 2 or distance_to_score >= 2:
        return "major_disagreement"
    if distance_to_expected == 1 or distance_to_score == 1:
        return "minor_disagreement"
    return "needs_review"


def label_from_score(score: float) -> str:
    if score >= 75:
        return "good"
    if score >= 50:
        return "medium"
    if score >= 25:
        return "weak"
    return "mismatch"


def analyze_synthetic_test_errors() -> dict[str, Any]:
    cases = load_synthetic_cases()
    _, test_cases = split_matching_cases(cases)
    confusion: Counter[tuple[str, str]] = Counter()
    category_confusion: dict[str, Counter[tuple[str, str]]] = defaultdict(Counter)
    detail_rows: list[dict[str, Any]] = []

    for case in test_cases:
        ml = predict_matching_fit(case)
        actual = str(case["fit_label"])
        predicted = str(ml.get("predicted_label") or "unavailable")
        confusion[(actual, predicted)] += 1
        category = str(case.get("category") or case.get("group") or "unknown")
        category_confusion[category][(actual, predicted)] += 1
        if actual != predicted:
            detail_rows.append({
                "case_id": case["case_id"],
                "category": category,
                "actual": actual,
                "predicted": predicted,
                "confidence": ml.get("confidence"),
            })

    top_category_errors = []
    for category, counter in sorted(category_confusion.items()):
        errors = sum(count for (actual, predicted), count in counter.items() if actual != predicted)
        total = sum(counter.values())
        top_category_errors.append({
            "category": category,
            "errors": errors,
            "total": total,
            "error_rate": round(errors / total, 3) if total else 0.0,
        })

    return {
        "test_size": len(test_cases),
        "confusion": {f"{actual}->{predicted}": count for (actual, predicted), count in sorted(confusion.items())},
        "good_predicted_medium": confusion[("good", "medium")],
        "mismatch_predicted_medium": confusion[("mismatch", "medium")],
        "medium_predicted_good": confusion[("medium", "good")],
        "medium_predicted_weak": confusion[("medium", "weak")],
        "medium_predicted_mismatch": confusion[("medium", "mismatch")],
        "category_errors": sorted(top_category_errors, key=lambda item: (-item["errors"], item["category"])),
        "disagreement_rows": detail_rows,
    }


def load_synthetic_cases() -> list[dict[str, Any]]:
    payload = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    cases = payload.get("cases", payload if isinstance(payload, list) else [])
    return [dict(case) for case in cases]


def build_phase_report(benchmark_rows: list[dict[str, Any]], synthetic_analysis: dict[str, Any]) -> str:
    table_rows = "\n".join(
        "| {case_id} | {scenario} | {expected_score_range} | {expected_label} | {rule_based_score} | {hybrid_score_candidate} | {ml_predicted_label} | {ml_confidence} | {agreement_status} |".format(
            **{
                **row,
                "ml_confidence": format_confidence(row["ml_confidence"]),
                "hybrid_score_candidate": row["hybrid_score_candidate"] if row["hybrid_score_candidate"] is not None else "n/a",
            }
        )
        for row in benchmark_rows
    )
    status_counts = Counter(row["agreement_status"] for row in benchmark_rows)
    status_text = ", ".join(f"{status}: {count}" for status, count in sorted(status_counts.items()))
    category_rows = "\n".join(
        f"| {item['category']} | {item['errors']} | {item['total']} | {item['error_rate']} |"
        for item in synthetic_analysis["category_errors"]
    )
    return f"""# Phase 9.1 - ML Benchmark & Disagreement Analysis

Date: 2026-06-22

## Mục tiêu

Đánh giá Trainable Matching Model V1 bằng benchmark U01-U10 và Synthetic Dataset V2. Phase này không train model mới, không thay production scoring và không đưa ML prediction thành điểm chính.

## U01-U10 comparison

| Case | Scenario | Expected range | Expected label | Rule score | Hybrid candidate | ML label | ML confidence | Agreement |
| --- | --- | --- | --- | ---: | ---: | --- | ---: | --- |
{table_rows}

## Disagreement summary

- Tổng trạng thái: {status_text}
- `aligned`: rule-based score, expected label và ML label cùng hướng.
- `minor_disagreement`: ML lệch một bậc so với expected/rule label.
- `major_disagreement`: ML lệch mạnh, cần review trước khi tin.
- `needs_review`: ML confidence thấp hoặc artifact không khả dụng.

## Synthetic Dataset V2 error analysis

- Test size: {synthetic_analysis['test_size']}
- `good -> medium`: {synthetic_analysis['good_predicted_medium']}
- `mismatch -> medium`: {synthetic_analysis['mismatch_predicted_medium']}
- `medium -> good`: {synthetic_analysis['medium_predicted_good']}
- `medium -> weak`: {synthetic_analysis['medium_predicted_weak']}
- `medium -> mismatch`: {synthetic_analysis['medium_predicted_mismatch']}

### Category error summary

| Category | Errors | Total test cases | Error rate |
| --- | ---: | ---: | ---: |
{category_rows}

## Model reliability assessment

ML V1 hữu ích như tín hiệu phụ để phát hiện disagreement, nhưng chưa đủ tin cậy để thay matcher hiện tại. Kết quả Phase 9.0 và Phase 9.1 cùng cho thấy model nhận diện `weak` khá ổn, nhưng còn dễ kéo `good` và `mismatch` về `medium`.

## Khi có thể tin ML

- Khi ML label trùng với rule-based score band và confidence đủ cao.
- Khi ML dùng để gợi ý case cần review nội bộ, không dùng trực tiếp cho user-facing score.
- Khi dữ liệu input giống format synthetic summary đã train.

## Khi không nên tin ML

- Khi ML confidence thấp.
- Khi ML label trái ngược mạnh với rule-based score hoặc benchmark expected label.
- Khi CV/JD là raw artifact dài, nhiễu, khác nhiều so với synthetic summary.
- Khi case liên quan career switch, same-role different-stack hoặc mismatch tinh tế.

## Recommendation trước Phase 9.2

1. Không promote ML V1 thành production score.
2. Dùng disagreement report để chọn case cần human review.
3. Bổ sung real anonymized beta labels cho boundary `good/medium` và `mismatch/medium`.
4. Nếu cải thiện model, ưu tiên dataset quality và label review trước khi đổi thuật toán.
5. Giữ rule-based matcher là source of truth cho user-facing score.
"""


def build_synthetic_error_report(synthetic_analysis: dict[str, Any]) -> str:
    confusion_rows = "\n".join(
        f"| {pair} | {count} |"
        for pair, count in synthetic_analysis["confusion"].items()
    )
    detail_rows = "\n".join(
        f"| {row['case_id']} | {row['category']} | {row['actual']} | {row['predicted']} | {format_confidence(row['confidence'])} |"
        for row in synthetic_analysis["disagreement_rows"][:50]
    )
    return f"""# ML Error Analysis V1

Date: 2026-06-22

## Scope

Phân tích lỗi của `matching_model_v1` trên test split deterministic của Synthetic Dataset V2. Script không train lại model, chỉ dùng artifact hiện có trong `backend/models/`.

## Confusion summary

| Actual -> Predicted | Count |
| --- | ---: |
{confusion_rows}

## Key errors

- `good -> medium`: {synthetic_analysis['good_predicted_medium']}
- `mismatch -> medium`: {synthetic_analysis['mismatch_predicted_medium']}
- `medium -> good`: {synthetic_analysis['medium_predicted_good']}
- `medium -> weak`: {synthetic_analysis['medium_predicted_weak']}
- `medium -> mismatch`: {synthetic_analysis['medium_predicted_mismatch']}

## Disagreement samples

| Case | Category | Actual | Predicted | Confidence |
| --- | --- | --- | --- | ---: |
{detail_rows}

## Ghi chú

ML V1 còn thiên về nhãn `medium` ở một số boundary case. Đây là tín hiệu cần cải thiện dataset và label review, chưa phải lý do để thay production scoring.
"""


def format_confidence(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"{float(value):.3f}"
    return "n/a"


if __name__ == "__main__":
    main()

