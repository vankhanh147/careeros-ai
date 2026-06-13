import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.career_profile import CareerProfile
from app.models.learning_roadmap import LearningRoadmap
from app.models.match_analysis import MatchAnalysis
from app.models.user import User
from app.schemas.roadmap import LearningRoadmapResponse, RoadmapGenerateRequest
from app.services.resume_job_matcher import analyze_resume_job_match
from app.services.roadmap_generator import build_roadmap_from_analysis, build_roadmap_from_profile
from app.services.security import get_current_user

router = APIRouter(prefix="/api/roadmaps", tags=["roadmaps"])


@router.post("/generate", response_model=LearningRoadmapResponse, status_code=status.HTTP_201_CREATED)
def generate_learning_roadmap(
    payload: RoadmapGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> LearningRoadmapResponse:
    profile = db.query(CareerProfile).filter(CareerProfile.user_id == current_user.id).first()
    timeline = (payload.timeline or "").strip() or (profile.timeline if profile else "")

    analysis = None
    if payload.analysis_id is not None:
        analysis = (
            db.query(MatchAnalysis)
            .filter(MatchAnalysis.id == payload.analysis_id, MatchAnalysis.user_id == current_user.id)
            .first()
        )
        if analysis is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")

    if analysis is None and profile is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cần có career profile hoặc chọn một analysis để tạo roadmap.",
        )

    if analysis is not None:
        resume_text = analysis.resume.extracted_text if analysis.resume else ""
        jd_text = analysis.job_description.content if analysis.job_description else ""
        analysis_result = analyze_resume_job_match(resume_text or "", jd_text or "")
        target_role = (profile.target_role if profile else "") or (
            analysis.job_description.title if analysis.job_description else ""
        )
        roadmap_data = build_roadmap_from_analysis(
            target_role=target_role,
            current_level=profile.current_level if profile else "",
            timeline=timeline,
            prioritized_missing_skills=_as_priority_dict(analysis_result["prioritized_missing_skills"]),
            improvement_plan=[str(item) for item in analysis_result["improvement_plan"]],
        )
    else:
        if _is_empty_profile(profile):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Career profile chưa đủ dữ liệu để tạo roadmap basic.",
            )
        roadmap_data = build_roadmap_from_profile(profile, timeline=timeline)

    roadmap = LearningRoadmap(
        user_id=current_user.id,
        analysis_id=analysis.id if analysis else None,
        title=str(roadmap_data["title"]),
        target_role=str(roadmap_data["target_role"]),
        timeline=str(roadmap_data["timeline"]),
        items=json.dumps(roadmap_data["items"], ensure_ascii=False),
        summary=str(roadmap_data["summary"]),
    )
    db.add(roadmap)
    db.commit()
    db.refresh(roadmap)
    return _to_response(roadmap)


@router.get("/me", response_model=list[LearningRoadmapResponse])
def get_my_roadmaps(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[LearningRoadmapResponse]:
    roadmaps = (
        db.query(LearningRoadmap)
        .filter(LearningRoadmap.user_id == current_user.id)
        .order_by(LearningRoadmap.created_at.desc())
        .limit(20)
        .all()
    )
    return [_to_response(roadmap) for roadmap in roadmaps]


@router.get("/{roadmap_id}", response_model=LearningRoadmapResponse)
def get_roadmap_by_id(
    roadmap_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> LearningRoadmapResponse:
    roadmap = (
        db.query(LearningRoadmap)
        .filter(LearningRoadmap.id == roadmap_id, LearningRoadmap.user_id == current_user.id)
        .first()
    )
    if roadmap is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found")
    return _to_response(roadmap)


def _to_response(roadmap: LearningRoadmap) -> LearningRoadmapResponse:
    return LearningRoadmapResponse(
        id=roadmap.id,
        user_id=roadmap.user_id,
        analysis_id=roadmap.analysis_id,
        title=roadmap.title,
        target_role=roadmap.target_role,
        timeline=roadmap.timeline,
        items=_load_items(roadmap.items),
        summary=roadmap.summary,
        created_at=roadmap.created_at,
        updated_at=roadmap.updated_at,
    )


def _load_items(value: str) -> list[dict[str, Any]]:
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return []
    if not isinstance(parsed, list):
        return []
    return [item for item in parsed if isinstance(item, dict)]


def _as_priority_dict(value: object) -> dict[str, list[str]]:
    if not isinstance(value, dict):
        return {"high_priority": [], "medium_priority": [], "low_priority": []}
    return {
        "high_priority": [str(item) for item in value.get("high_priority", [])],
        "medium_priority": [str(item) for item in value.get("medium_priority", [])],
        "low_priority": [str(item) for item in value.get("low_priority", [])],
    }


def _is_empty_profile(profile: CareerProfile | None) -> bool:
    if profile is None:
        return True
    fields = [
        profile.target_role,
        profile.current_level,
        profile.skills,
        profile.experience_summary,
        profile.projects_summary,
        profile.career_goal,
    ]
    return not any((value or "").strip() for value in fields)