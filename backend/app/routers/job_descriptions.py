from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.job_description import JobDescription
from app.models.user import User
from app.schemas.job_description import JobDescriptionCreateRequest, JobDescriptionResponse
from app.services.security import get_current_user

router = APIRouter(prefix="/api/job-descriptions", tags=["job-descriptions"])


@router.post("", response_model=JobDescriptionResponse, status_code=status.HTTP_201_CREATED)
def create_job_description(
    payload: JobDescriptionCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JobDescription:
    job_description = JobDescription(
        user_id=current_user.id,
        title=payload.title,
        company=payload.company,
        content=payload.content,
        source_url=payload.source_url,
    )
    db.add(job_description)
    db.commit()
    db.refresh(job_description)
    return job_description


@router.get("/me", response_model=list[JobDescriptionResponse])
def get_my_job_descriptions(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[JobDescription]:
    return (
        db.query(JobDescription)
        .filter(JobDescription.user_id == current_user.id)
        .order_by(JobDescription.created_at.desc())
        .all()
    )
