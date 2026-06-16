import json
from collections import Counter
from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy import distinct, func
from sqlalchemy.orm import Session

from app.core.errors import raise_app_error
from app.database import get_db
from app.models.career_profile import CareerProfile
from app.models.interview import InterviewSession
from app.models.job_description import JobDescription
from app.models.learning_roadmap import LearningRoadmap
from app.models.match_analysis import MatchAnalysis
from app.models.resume import Resume
from app.models.user import User
from app.models.user_feedback import UserFeedback
from app.schemas.founder_insights import (
    CommonMissingSkill,
    FeedbackTypeSummary,
    FounderInsightsResponse,
    FunnelUsage,
    LearningLoopSummary,
    MatchHealthSummary,
)
from app.services.resume_job_matcher import analyze_resume_job_match
from app.services.security import get_current_user

router = APIRouter(prefix="/api/founder", tags=["founder"])
FOUNDER_ROLES = {"founder", "admin"}
FEEDBACK_TYPES = ("analysis", "roadmap", "interview")


@router.get("/insights", response_model=FounderInsightsResponse)
def get_founder_insights(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> FounderInsightsResponse:
    _require_founder(current_user)
    analyses = db.query(MatchAnalysis).all()
    roadmaps = db.query(LearningRoadmap).all()

    return FounderInsightsResponse(
        funnel=_build_funnel(db),
        feedback=_build_feedback_summary(db),
        common_missing_skills=_build_common_missing_skills(analyses),
        match_health=_build_match_health(analyses),
        learning_loop=_build_learning_loop(analyses, roadmaps),
    )


def _require_founder(user: User) -> None:
    if (user.role or "").lower() not in FOUNDER_ROLES:
        raise_app_error(status.HTTP_403_FORBIDDEN, "Founder access required", "FOUNDER_ACCESS_REQUIRED")


def _build_funnel(db: Session) -> FunnelUsage:
    profiles = db.query(CareerProfile).all()
    return FunnelUsage(
        registered_users=db.query(User).count(),
        profile_completed_users=sum(1 for profile in profiles if _has_profile_data(profile)),
        uploaded_cv_users=_distinct_user_count(db, Resume.user_id),
        uploaded_jd_users=_distinct_user_count(db, JobDescription.user_id),
        generated_analysis_users=_distinct_user_count(db, MatchAnalysis.user_id),
        generated_roadmap_users=_distinct_user_count(db, LearningRoadmap.user_id),
        started_interview_users=_distinct_user_count(db, InterviewSession.user_id),
        completed_interview_users=db.query(func.count(distinct(InterviewSession.user_id))).filter(InterviewSession.status == "finished").scalar() or 0,
    )


def _distinct_user_count(db: Session, column: Any) -> int:
    return db.query(func.count(distinct(column))).scalar() or 0


def _has_profile_data(profile: CareerProfile | None) -> bool:
    if profile is None:
        return False
    fields = [
        profile.target_role,
        profile.current_level,
        profile.skills,
        profile.experience_summary,
        profile.projects_summary,
        profile.career_goal,
        profile.timeline,
    ]
    return any((value or "").strip() for value in fields)


def _build_feedback_summary(db: Session) -> list[FeedbackTypeSummary]:
    summaries = []
    for feedback_type in FEEDBACK_TYPES:
        total = db.query(UserFeedback).filter(UserFeedback.feedback_type == feedback_type).count()
        useful = db.query(UserFeedback).filter(UserFeedback.feedback_type == feedback_type, UserFeedback.useful.is_(True)).count()
        not_useful = max(total - useful, 0)
        useful_rate = round((useful / total) * 100, 1) if total else 0
        summaries.append(
            FeedbackTypeSummary(
                feedback_type=feedback_type,
                total=total,
                useful=useful,
                not_useful=not_useful,
                useful_rate=useful_rate,
            )
        )
    return summaries


def _build_common_missing_skills(analyses: list[MatchAnalysis]) -> list[CommonMissingSkill]:
    counter: Counter[str] = Counter()
    for analysis in analyses:
        for skill in _load_json_list(analysis.missing_skills):
            normalized = skill.strip().lower()
            if normalized:
                counter[normalized] += 1
    return [CommonMissingSkill(skill=skill, count=count) for skill, count in counter.most_common(10)]


def _build_match_health(analyses: list[MatchAnalysis]) -> MatchHealthSummary:
    total = len(analyses)
    average_score = round(sum(float(item.match_score) for item in analyses) / total, 1) if total else 0
    confidence_counts = {"high": 0, "medium": 0, "low": 0, "unknown": 0}

    for analysis in analyses:
        confidence = _analysis_confidence(analysis)
        if confidence not in confidence_counts:
            confidence = "unknown"
        confidence_counts[confidence] += 1

    return MatchHealthSummary(
        total_analyses=total,
        average_match_score=average_score,
        high_confidence_cases=confidence_counts["high"],
        medium_confidence_cases=confidence_counts["medium"],
        low_confidence_cases=confidence_counts["low"],
        unknown_confidence_cases=confidence_counts["unknown"],
    )


def _analysis_confidence(analysis: MatchAnalysis) -> str:
    try:
        resume_text = analysis.resume.extracted_text if analysis.resume else ""
        jd_text = analysis.job_description.content if analysis.job_description else ""
        result = analyze_resume_job_match(resume_text or "", jd_text or "")
        scoring_breakdown = result.get("scoring_breakdown", {})
        if isinstance(scoring_breakdown, dict):
            return str(scoring_breakdown.get("confidence") or "unknown").lower()
    except Exception:
        return "unknown"
    return "unknown"


def _build_learning_loop(analyses: list[MatchAnalysis], roadmaps: list[LearningRoadmap]) -> LearningLoopSummary:
    users_with_completed_items: set[int] = set()
    completed_items_total = 0
    roadmap_refs_by_user: dict[int, list[tuple[Any, int | None]]] = {}

    for roadmap in roadmaps:
        roadmap_refs_by_user.setdefault(roadmap.user_id, []).append((roadmap.created_at, roadmap.analysis_id))
        completed_count = _completed_item_count(roadmap)
        if completed_count > 0:
            users_with_completed_items.add(roadmap.user_id)
            completed_items_total += completed_count

    users_rerunning_analysis_after_roadmap: set[int] = set()
    for analysis in analyses:
        for roadmap_created_at, source_analysis_id in roadmap_refs_by_user.get(analysis.user_id, []):
            if source_analysis_id is not None and analysis.id > source_analysis_id:
                users_rerunning_analysis_after_roadmap.add(analysis.user_id)
                break
            if source_analysis_id is None and analysis.created_at > roadmap_created_at:
                users_rerunning_analysis_after_roadmap.add(analysis.user_id)
                break

    return LearningLoopSummary(
        users_completing_roadmap_items=len(users_with_completed_items),
        completed_roadmap_items=completed_items_total,
        users_rerunning_analysis_after_roadmap=len(users_rerunning_analysis_after_roadmap),
    )


def _completed_item_count(roadmap: LearningRoadmap) -> int:
    try:
        parsed = json.loads(roadmap.items)
    except (TypeError, json.JSONDecodeError):
        return 0
    if not isinstance(parsed, list):
        return 0
    return sum(1 for item in parsed if isinstance(item, dict) and item.get("completed") is True)


def _load_json_list(value: str) -> list[str]:
    try:
        parsed = json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return []
    if not isinstance(parsed, list):
        return []
    return [str(item) for item in parsed]
