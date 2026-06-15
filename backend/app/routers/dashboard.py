import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.career_profile import CareerProfile
from app.models.interview import InterviewSession
from app.models.job_description import JobDescription
from app.models.learning_roadmap import LearningRoadmap
from app.models.match_analysis import MatchAnalysis
from app.models.resume import Resume
from app.models.usage_event import UsageEvent
from app.models.user import User
from app.models.user_feedback import UserFeedback
from app.schemas.dashboard import (
    DashboardLatestAnalysis,
    DashboardLatestInterview,
    DashboardLatestRoadmap,
    DashboardSummaryResponse,
    DashboardUserInfo,
)
from app.schemas.usage import UsageSummaryResponse
from app.services.resume_job_matcher import analyze_resume_job_match
from app.services.security import get_current_user
from app.services.usage_tracking import (
    EVENT_ANALYSIS_GENERATED,
    EVENT_INTERVIEW_STARTED,
    EVENT_RESUME_UPLOADED,
    EVENT_ROADMAP_GENERATED,
)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> DashboardSummaryResponse:
    profile = db.query(CareerProfile).filter(CareerProfile.user_id == current_user.id).first()
    resume_count = db.query(Resume).filter(Resume.user_id == current_user.id).count()
    job_description_count = db.query(JobDescription).filter(JobDescription.user_id == current_user.id).count()

    latest_resume = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id)
        .order_by(Resume.created_at.desc(), Resume.id.desc())
        .first()
    )
    latest_analysis = (
        db.query(MatchAnalysis)
        .filter(MatchAnalysis.user_id == current_user.id)
        .order_by(MatchAnalysis.created_at.desc(), MatchAnalysis.id.desc())
        .first()
    )
    latest_roadmap = (
        db.query(LearningRoadmap)
        .filter(LearningRoadmap.user_id == current_user.id)
        .order_by(LearningRoadmap.created_at.desc())
        .first()
    )
    latest_interview = (
        db.query(InterviewSession)
        .filter(InterviewSession.user_id == current_user.id)
        .order_by(InterviewSession.created_at.desc())
        .first()
    )

    profile_has_data = _has_profile_data(profile)
    roadmap_progress = _roadmap_progress(latest_roadmap)
    has_new_resume_after_analysis = bool(
        latest_resume is not None
        and latest_analysis is not None
        and (
            latest_resume.created_at > latest_analysis.created_at
            or (latest_resume.created_at == latest_analysis.created_at and latest_resume.id != latest_analysis.resume_id)
        )
    )
    should_rerun_analysis = bool(has_new_resume_after_analysis or roadmap_progress["completed_items"] > 0)

    return DashboardSummaryResponse(
        user=DashboardUserInfo(
            id=current_user.id,
            email=current_user.email,
            full_name=current_user.full_name,
            role=current_user.role,
            is_active=current_user.is_active,
        ),
        has_career_profile=profile_has_data,
        resume_count=resume_count,
        job_description_count=job_description_count,
        latest_analysis=_to_latest_analysis(latest_analysis),
        latest_roadmap=_to_latest_roadmap(latest_roadmap),
        latest_interview=_to_latest_interview(latest_interview),
        recommended_next_actions=_recommended_next_actions(
            has_profile=profile_has_data,
            resume_count=resume_count,
            job_description_count=job_description_count,
            has_analysis=latest_analysis is not None,
            has_roadmap=latest_roadmap is not None,
            has_interview=latest_interview is not None,
            has_new_resume_after_analysis=has_new_resume_after_analysis,
            roadmap_completed_items=roadmap_progress["completed_items"],
        ),
        has_new_resume_after_analysis=has_new_resume_after_analysis,
        should_rerun_analysis=should_rerun_analysis,
        learning_loop_summary=_learning_loop_summary(roadmap_progress),
    )


@router.get("/usage-summary", response_model=UsageSummaryResponse)
def get_usage_summary(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> UsageSummaryResponse:
    return UsageSummaryResponse(
        total_resume_uploads=_count_usage_events(db, current_user.id, EVENT_RESUME_UPLOADED),
        total_analysis=_count_usage_events(db, current_user.id, EVENT_ANALYSIS_GENERATED),
        total_roadmaps=_count_usage_events(db, current_user.id, EVENT_ROADMAP_GENERATED),
        total_interviews=_count_usage_events(db, current_user.id, EVENT_INTERVIEW_STARTED),
        total_feedback=db.query(UserFeedback).filter(UserFeedback.user_id == current_user.id).count(),
    )


def _count_usage_events(db: Session, user_id: int, event_type: str) -> int:
    return db.query(UsageEvent).filter(UsageEvent.user_id == user_id, UsageEvent.event_type == event_type).count()


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


def _to_latest_analysis(analysis: MatchAnalysis | None) -> DashboardLatestAnalysis | None:
    if analysis is None:
        return None
    return DashboardLatestAnalysis(
        match_score=analysis.match_score,
        skill_gap_summary=_safe_skill_gap_summary(analysis),
        created_at=analysis.created_at,
    )


def _to_latest_roadmap(roadmap: LearningRoadmap | None) -> DashboardLatestRoadmap | None:
    if roadmap is None:
        return None
    progress = _roadmap_progress(roadmap)
    return DashboardLatestRoadmap(
        title=roadmap.title,
        timeline=roadmap.timeline,
        created_at=roadmap.created_at,
        completed_items=progress["completed_items"],
        total_items=progress["total_items"],
    )


def _to_latest_interview(interview: InterviewSession | None) -> DashboardLatestInterview | None:
    if interview is None:
        return None
    return DashboardLatestInterview(
        target_role=interview.target_role,
        status=interview.status,
        score=interview.score,
        created_at=interview.created_at,
    )


def _safe_skill_gap_summary(analysis: MatchAnalysis) -> str:
    try:
        resume_text = analysis.resume.extracted_text if analysis.resume else ""
        jd_text = analysis.job_description.content if analysis.job_description else ""
        if resume_text or jd_text:
            result = analyze_resume_job_match(resume_text or "", jd_text or "")
            return str(result.get("skill_gap_summary") or analysis.summary)
    except Exception:
        pass
    return analysis.summary or "Ch\u01b0a c\u00f3 skill gap summary kh\u1ea3 d\u1ee5ng."


def _roadmap_progress(roadmap: LearningRoadmap | None) -> dict[str, int]:
    if roadmap is None:
        return {"completed_items": 0, "total_items": 0}
    items = _load_roadmap_items(roadmap.items)
    return {
        "completed_items": sum(1 for item in items if item.get("completed") is True),
        "total_items": len(items),
    }


def _load_roadmap_items(value: str) -> list[dict]:
    try:
        parsed = json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return []
    if not isinstance(parsed, list):
        return []
    return [item for item in parsed if isinstance(item, dict)]


def _learning_loop_summary(progress: dict[str, int]) -> str | None:
    total = progress.get("total_items", 0)
    if total <= 0:
        return None
    completed = progress.get("completed_items", 0)
    return f"\u0110\u00e3 ho\u00e0n th\u00e0nh {completed}/{total} m\u1ee5c roadmap"


def _recommended_next_actions(
    *,
    has_profile: bool,
    resume_count: int,
    job_description_count: int,
    has_analysis: bool,
    has_roadmap: bool,
    has_interview: bool,
    has_new_resume_after_analysis: bool,
    roadmap_completed_items: int,
) -> list[str]:
    actions = []
    if not has_profile:
        actions.append("Ho\u00e0n thi\u1ec7n h\u1ed3 s\u01a1 ngh\u1ec1 nghi\u1ec7p")
    if resume_count == 0 or job_description_count == 0:
        actions.append("Upload CV v\u00e0 th\u00eam Job Description")
    if resume_count > 0 and job_description_count > 0 and not has_analysis:
        actions.append("Ch\u1ea1y Resume \u2194 JD Matching")
    if resume_count > 0 and job_description_count > 0 and has_new_resume_after_analysis:
        actions.append("B\u1ea1n \u0111\u00e3 c\u1eadp nh\u1eadt CV m\u1edbi. N\u00ean ch\u1ea1y l\u1ea1i ph\u00e2n t\u00edch CV \u2194 JD.")
    if has_analysis and not has_roadmap:
        actions.append("T\u1ea1o roadmap h\u1ecdc t\u1eadp")
    if has_analysis and has_roadmap and not has_interview:
        actions.append("B\u1ea1n \u0111\u00e3 c\u00f3 roadmap h\u1ecdc t\u1eadp. H\u00e3y luy\u1ec7n Mock Interview \u0111\u1ec3 ki\u1ec3m tra ti\u1ebfn b\u1ed9.")
    if has_roadmap and roadmap_completed_items > 0:
        actions.append("B\u1ea1n \u0111\u00e3 ho\u00e0n th\u00e0nh m\u1ed9t ph\u1ea7n roadmap. H\u00e3y c\u1eadp nh\u1eadt CV v\u00e0 ch\u1ea1y l\u1ea1i matching.")
    if has_roadmap and not has_interview:
        actions.append("Luy\u1ec7n mock interview")
    if not actions:
        actions.append("Ti\u1ebfp t\u1ee5c c\u1ea3i thi\u1ec7n CV ho\u1eb7c th\u1eed JD m\u1edbi")
    return actions
