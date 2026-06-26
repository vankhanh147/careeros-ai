"""Run an offline training job through the CareerOS AI training contract.

Training job này chỉ đọc dataset artifact đã assembly và manifest. Script không
đọc trực tiếp synthetic/raw benchmark/beta sources, không thay production
scoring và không tích hợp model vào runtime.
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

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split


ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.ml.features import build_feature_corpus
from app.ml.training_infra import parse_training_config


CONFIG_PATH = BACKEND_DIR / "ml" / "configs" / "training_config.json"
DATASET_ARTIFACT_PATH = BACKEND_DIR / "ml" / "datasets" / "training_dataset_v3.json"
DATASET_MANIFEST_PATH = BACKEND_DIR / "ml" / "datasets" / "training_dataset_manifest.json"
MODELS_DIR = BACKEND_DIR / "ml" / "models"
EXPERIMENTS_DIR = BACKEND_DIR / "ml" / "experiments"
REGISTRY_DIR = BACKEND_DIR / "ml" / "registry"
REPORTS_DIR = BACKEND_DIR / "ml" / "reports"

VALID_LABELS = {"good", "medium", "weak", "mismatch"}
REQUIRED_CONFIG_FIELDS = {"model_name", "model_version"}
MOJIBAKE_PATTERN = re.compile(
    r"\u00c3|\u00c2|\u00e1\u00ba|\u00e1\u00bb|\u00c4|\u00c6|\u00c5|\ufffd|M\?|Kh\?|H\?\?|tr\?|\?\?\?"
)
EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_PATTERN = re.compile(r"(?<!\d)(?:\+?\d[\d\s().-]{8,}\d)(?!\d)")
ISO_TIMESTAMP_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z?")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def stable_json(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def calculate_artifact_hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(stable_json(payload).encode("utf-8")).hexdigest()


def load_training_job_config(path: Path = CONFIG_PATH) -> dict[str, Any]:
    config = parse_training_config(path)
    missing = sorted(field for field in REQUIRED_CONFIG_FIELDS if field not in config)
    if missing:
        raise ValueError(f"training config thiếu field bắt buộc: {', '.join(missing)}")
    if not str(config["model_name"]).strip():
        raise ValueError("model_name không được rỗng.")
    if not str(config["model_version"]).strip():
        raise ValueError("model_version không được rỗng.")
    if str(config["classifier"]) != "LogisticRegression":
        raise ValueError("Phase 10.4 chỉ hỗ trợ LogisticRegression trong training job contract.")
    return config


def load_training_dataset(path: Path = DATASET_ARTIFACT_PATH) -> dict[str, Any]:
    if not path.exists():
        raise ValueError(f"Không tìm thấy dataset artifact: {path}")
    payload = read_json(path)
    if not isinstance(payload, dict):
        raise ValueError("Dataset artifact phải là JSON object.")
    return payload


def load_manifest(path: Path = DATASET_MANIFEST_PATH) -> dict[str, Any]:
    if not path.exists():
        raise ValueError(f"Không tìm thấy dataset manifest: {path}")
    payload = read_json(path)
    if not isinstance(payload, dict):
        raise ValueError("Dataset manifest phải là JSON object.")
    return payload


def validate_dataset_contract(
    *,
    config: dict[str, Any],
    dataset: dict[str, Any],
    manifest: dict[str, Any],
    registry_dir: Path = REGISTRY_DIR,
    models_dir: Path = MODELS_DIR,
) -> None:
    cases = dataset.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("Dataset artifact rỗng hoặc thiếu field cases.")
    dataset_version = str(dataset.get("dataset_version") or "")
    manifest_version = str(manifest.get("dataset_version") or "")
    config_version = str(config.get("dataset_version") or "")
    if dataset_version != manifest_version or dataset_version != config_version:
        raise ValueError("dataset_version không khớp giữa config, artifact và manifest.")
    expected_hash = str(manifest.get("artifact_hash") or "")
    actual_hash = calculate_artifact_hash(dataset)
    if not expected_hash or actual_hash != expected_hash:
        raise ValueError("artifact_hash không khớp manifest.")

    model_version = str(config["model_version"])
    if (registry_dir / f"{model_version}.json").exists():
        raise ValueError(f"model_version đã tồn tại trong registry: {model_version}")
    if (models_dir / model_version).exists():
        raise ValueError(f"model_version đã có artifact directory: {model_version}")

    ids: Counter[str] = Counter()
    for index, case in enumerate(cases, start=1):
        case_id = str(case.get("case_id") or "").strip()
        label = str(case.get("fit_label") or "").strip()
        serialized = json.dumps({key: value for key, value in case.items() if key != "content_hash"}, ensure_ascii=False)
        if not case_id:
            raise ValueError(f"Case #{index} thiếu case_id.")
        ids[case_id] += 1
        if label not in VALID_LABELS:
            raise ValueError(f"{case_id}: label không hợp lệ: {label}.")
        if MOJIBAKE_PATTERN.search(serialized):
            raise ValueError(f"{case_id}: có dấu hiệu mojibake.")
        pii_scan_text = ISO_TIMESTAMP_PATTERN.sub("", serialized)
        if EMAIL_PATTERN.search(serialized) or PHONE_PATTERN.search(pii_scan_text):
            raise ValueError(f"{case_id}: có dấu hiệu PII.")
    duplicate_ids = sorted(case_id for case_id, count in ids.items() if count > 1)
    if duplicate_ids:
        raise ValueError(f"case_id bị trùng: {', '.join(duplicate_ids)}.")


def build_run_id(model_version: str, timestamp: datetime) -> str:
    return f"{model_version}_{timestamp.strftime('%Y%m%dT%H%M%SZ')}"


def train_model(cases: list[dict[str, Any]], config: dict[str, Any]) -> dict[str, Any]:
    labels = [str(case["fit_label"]) for case in cases]
    test_size = float(config["split_ratio"]["test"])
    random_seed = int(config["random_seed"])
    label_counts = Counter(labels)
    class_count = len(label_counts)
    test_count = max(1, int(round(len(cases) * test_size)))
    train_count = len(cases) - test_count
    can_stratify = min(label_counts.values()) >= 2 and test_count >= class_count and train_count >= class_count
    stratify = labels if can_stratify else None
    train_cases, test_cases = train_test_split(
        cases,
        test_size=test_size,
        random_state=random_seed,
        stratify=stratify,
    )
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=5000, min_df=1)
    train_features = vectorizer.fit_transform(build_feature_corpus(train_cases))
    test_features = vectorizer.transform(build_feature_corpus(test_cases))
    model = LogisticRegression(max_iter=1000, random_state=random_seed, class_weight="balanced")
    model.fit(train_features, [str(case["fit_label"]) for case in train_cases])
    predictions = [str(prediction) for prediction in model.predict(test_features)]
    expected = [str(case["fit_label"]) for case in test_cases]
    labels_order = sorted(VALID_LABELS)
    metrics = {
        "accuracy": float(accuracy_score(expected, predictions)),
        "macro_f1": float(f1_score(expected, predictions, average="macro", zero_division=0)),
        "classification_report": classification_report(
            expected,
            predictions,
            labels=labels_order,
            output_dict=True,
            zero_division=0,
        ),
        "confusion_matrix": confusion_matrix(expected, predictions, labels=labels_order).tolist(),
        "labels": labels_order,
        "train_size": len(train_cases),
        "test_size": len(test_cases),
    }
    return {
        "model": model,
        "vectorizer": vectorizer,
        "labels": labels_order,
        "metrics": metrics,
        "train_cases": train_cases,
        "test_cases": test_cases,
    }


def build_metadata(
    *,
    config: dict[str, Any],
    manifest: dict[str, Any],
    run_id: str,
    started_at: datetime,
    finished_at: datetime | None,
    status: str,
    metrics: dict[str, Any] | None,
    artifact_paths: dict[str, str],
) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "dataset_version": config["dataset_version"],
        "dataset_hash": manifest["artifact_hash"],
        "feature_version": config["feature_version"],
        "model_name": config["model_name"],
        "model_version": config["model_version"],
        "classifier": config["classifier"],
        "training_started_at": started_at.isoformat(),
        "training_finished_at": finished_at.isoformat() if finished_at else None,
        "metrics": metrics or {},
        "artifact_paths": artifact_paths,
        "status": status,
        "production_safe": False,
    }


def run_training_job(
    *,
    config_path: Path = CONFIG_PATH,
    dataset_path: Path = DATASET_ARTIFACT_PATH,
    manifest_path: Path = DATASET_MANIFEST_PATH,
    models_dir: Path = MODELS_DIR,
    experiments_dir: Path = EXPERIMENTS_DIR,
    registry_dir: Path = REGISTRY_DIR,
    reports_dir: Path = REPORTS_DIR,
    dry_run: bool = False,
) -> dict[str, Any]:
    config = load_training_job_config(config_path)
    dataset = load_training_dataset(dataset_path)
    manifest = load_manifest(manifest_path)
    validate_dataset_contract(
        config=config,
        dataset=dataset,
        manifest=manifest,
        registry_dir=registry_dir,
        models_dir=models_dir,
    )

    started_at = datetime.now(timezone.utc)
    run_id = build_run_id(str(config["model_version"]), started_at)
    model_dir = models_dir / str(config["model_version"])
    artifact_paths = {
        "model": str(model_dir / "model.joblib"),
        "vectorizer": str(model_dir / "vectorizer.joblib"),
        "labels": str(model_dir / "labels.json"),
        "model_metadata": str(model_dir / "model_metadata.json"),
        "experiment": str(experiments_dir / f"{run_id}.json"),
        "registry": str(registry_dir / f"{config['model_version']}.json"),
        "evaluation_report": str(reports_dir / f"{run_id}_evaluation.json"),
    }
    if dry_run:
        metadata = build_metadata(
            config=config,
            manifest=manifest,
            run_id=run_id,
            started_at=started_at,
            finished_at=None,
            status="dry_run",
            metrics=None,
            artifact_paths=artifact_paths,
        )
        return {
            "ok": True,
            "dry_run": True,
            "config": config,
            "case_count": len(dataset["cases"]),
            "metadata": metadata,
        }

    trained = train_model(list(dataset["cases"]), config)
    finished_at = datetime.now(timezone.utc)
    metadata = build_metadata(
        config=config,
        manifest=manifest,
        run_id=run_id,
        started_at=started_at,
        finished_at=finished_at,
        status="completed",
        metrics=trained["metrics"],
        artifact_paths=artifact_paths,
    )

    model_dir.mkdir(parents=True, exist_ok=False)
    joblib.dump(trained["model"], model_dir / "model.joblib")
    joblib.dump(trained["vectorizer"], model_dir / "vectorizer.joblib")
    write_json(model_dir / "labels.json", {"labels": trained["labels"]})
    write_json(model_dir / "model_metadata.json", metadata)
    write_json(Path(artifact_paths["experiment"]), metadata)
    registry_record = {
        "model_name": config["model_name"],
        "model_version": config["model_version"],
        "dataset_version": config["dataset_version"],
        "dataset_hash": manifest["artifact_hash"],
        "feature_version": config["feature_version"],
        "accuracy": trained["metrics"]["accuracy"],
        "macro_f1": trained["metrics"]["macro_f1"],
        "created_at": finished_at.isoformat(),
        "training_command": "python scripts/run_training_job.py",
        "artifact_paths": artifact_paths,
        "status": "draft",
        "production_safe": False,
        "notes": "Registry draft tạo từ Training Job Contract; chưa dùng cho production scoring.",
    }
    write_json(Path(artifact_paths["registry"]), registry_record)
    write_json(Path(artifact_paths["evaluation_report"]), metadata)
    return {"ok": True, "dry_run": False, "metadata": metadata, "metrics": trained["metrics"]}


def print_summary(result: dict[str, Any]) -> None:
    metadata = result["metadata"]
    print("CareerOS AI Training Job")
    print("=" * 40)
    print(f"Run ID: {metadata['run_id']}")
    print(f"Dataset version: {metadata['dataset_version']}")
    print(f"Dataset hash: {metadata['dataset_hash']}")
    print(f"Model version: {metadata['model_version']}")
    print(f"Status: {metadata['status']}")
    if result.get("dry_run"):
        print(f"Dry-run: hợp lệ, chưa ghi artifact. Cases: {result['case_count']}")
    else:
        metrics = metadata["metrics"]
        print(f"Accuracy: {metrics['accuracy']:.3f}")
        print(f"Macro F1: {metrics['macro_f1']:.3f}")
        print("Artifacts:")
        for label, path in metadata["artifact_paths"].items():
            print(f"  - {label}: {path}")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Run CareerOS AI offline training job.")
    parser.add_argument("--dry-run", action="store_true", help="Validate contract và in kế hoạch, không ghi artifact.")
    args = parser.parse_args()
    try:
        result = run_training_job(dry_run=args.dry_run)
    except Exception as exc:  # noqa: BLE001 - CLI cần trả lỗi rõ ràng.
        print(f"Training job failed: {exc}", file=sys.stderr)
        return 1
    print_summary(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
