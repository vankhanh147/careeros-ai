"""Parallel semantic matching helpers for CareerOS AI.

Phase 8.3 keeps semantic matching as an evaluation signal. This module must not
change production scoring by itself and must not import sentence-transformers
unless semantic matching is explicitly enabled.
"""

from __future__ import annotations

import os
import re
from typing import Any, TypedDict

DEFAULT_SEMANTIC_MODEL_NAME = "all-MiniLM-L6-v2"
MIN_TEXT_LENGTH_FOR_SEMANTIC = 80
_SEMANTIC_MODEL: Any | None = None
_SEMANTIC_MODEL_LOAD_ERROR: str | None = None


class SemanticInsights(TypedDict):
    enabled: bool
    model_name: str | None
    resume_jd_similarity: float | None
    confidence: str
    notes: list[str]
    reason: str | None


def build_semantic_insights(resume_text: str, job_description_text: str) -> SemanticInsights:
    """Return semantic metadata without mutating matcher score."""

    resume_text = resume_text or ""
    job_description_text = job_description_text or ""
    model_name = semantic_model_name()

    if not sentence_transformers_enabled():
        return _disabled_insight(model_name, "semantic model disabled")

    if not _has_enough_text(resume_text, job_description_text):
        return {
            "enabled": False,
            "model_name": model_name,
            "resume_jd_similarity": None,
            "confidence": "low",
            "notes": ["Chưa đủ dữ liệu text để tính semantic similarity đáng tin cậy."],
            "reason": "text too short",
        }

    model = get_semantic_model()
    if model is None:
        return {
            "enabled": False,
            "model_name": model_name,
            "resume_jd_similarity": None,
            "confidence": "low",
            "notes": ["Semantic model không khả dụng, hệ thống giữ fallback rule-based."],
            "reason": _SEMANTIC_MODEL_LOAD_ERROR or "semantic model unavailable",
        }

    similarity = _compute_similarity(model, resume_text, job_description_text)
    if similarity is None:
        return {
            "enabled": False,
            "model_name": model_name,
            "resume_jd_similarity": None,
            "confidence": "low",
            "notes": ["Không thể tính semantic similarity trong lần phân tích này."],
            "reason": "semantic similarity failed",
        }

    return {
        "enabled": True,
        "model_name": model_name,
        "resume_jd_similarity": similarity,
        "confidence": _semantic_confidence(resume_text, job_description_text, similarity),
        "notes": _semantic_notes(similarity),
        "reason": None,
    }


def get_semantic_model() -> Any | None:
    """Lazy-load SentenceTransformer only when explicitly enabled."""

    global _SEMANTIC_MODEL, _SEMANTIC_MODEL_LOAD_ERROR

    if not sentence_transformers_enabled():
        return None
    if _SEMANTIC_MODEL is not None:
        return _SEMANTIC_MODEL
    if _SEMANTIC_MODEL_LOAD_ERROR is not None:
        return None

    try:
        from sentence_transformers import SentenceTransformer

        local_files_only = os.getenv("SENTENCE_TRANSFORMERS_LOCAL_FILES_ONLY", "true").strip().lower() != "false"
        _SEMANTIC_MODEL = SentenceTransformer(semantic_model_name(), local_files_only=local_files_only)
        return _SEMANTIC_MODEL
    except Exception as exc:  # pragma: no cover - exact failure depends on optional local model state
        _SEMANTIC_MODEL_LOAD_ERROR = str(exc)
        return None


def reset_semantic_model_cache() -> None:
    """Test helper to reset lazy model state."""

    global _SEMANTIC_MODEL, _SEMANTIC_MODEL_LOAD_ERROR
    _SEMANTIC_MODEL = None
    _SEMANTIC_MODEL_LOAD_ERROR = None


def sentence_transformers_enabled() -> bool:
    return os.getenv("SENTENCE_TRANSFORMERS_ENABLED", "false").strip().lower() == "true"


def semantic_model_name() -> str:
    return os.getenv("SENTENCE_TRANSFORMERS_MODEL_NAME", DEFAULT_SEMANTIC_MODEL_NAME).strip() or DEFAULT_SEMANTIC_MODEL_NAME


def _compute_similarity(model: Any, resume_text: str, job_description_text: str) -> float | None:
    try:
        embeddings = model.encode(
            [_semantic_input(resume_text), _semantic_input(job_description_text)],
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        cosine_similarity = float(embeddings[0] @ embeddings[1])
        return round(max(0.0, min(1.0, cosine_similarity)), 4)
    except Exception:
        return None


def _semantic_input(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", (text or "")).strip()
    return cleaned[:6000]


def _has_enough_text(resume_text: str, job_description_text: str) -> bool:
    return len(resume_text.strip()) >= MIN_TEXT_LENGTH_FOR_SEMANTIC and len(job_description_text.strip()) >= MIN_TEXT_LENGTH_FOR_SEMANTIC


def _semantic_confidence(resume_text: str, job_description_text: str, similarity: float) -> str:
    if len(resume_text.strip()) < 400 or len(job_description_text.strip()) < 200:
        return "low"
    if len(resume_text.strip()) >= 1000 and len(job_description_text.strip()) >= 500 and similarity >= 0.45:
        return "high"
    return "medium"


def _semantic_notes(similarity: float) -> list[str]:
    if similarity >= 0.7:
        return ["CV và JD có mức tương đồng ngữ nghĩa cao. Vẫn cần kiểm tra skill gap và evidence cụ thể."]
    if similarity >= 0.45:
        return ["CV và JD có một phần ngữ cảnh tương đồng. Nên đọc cùng role alignment, stack gap và critical skills."]
    return ["Semantic similarity thấp. CV có thể đang mô tả kinh nghiệm lệch ngữ cảnh so với JD hoặc thiếu mô tả project liên quan."]


def _disabled_insight(model_name: str, reason: str) -> SemanticInsights:
    return {
        "enabled": False,
        "model_name": model_name,
        "resume_jd_similarity": None,
        "confidence": "low",
        "notes": ["Semantic matching đang tắt; kết quả hiện dùng rule-based scoring và taxonomy metadata."],
        "reason": reason,
    }