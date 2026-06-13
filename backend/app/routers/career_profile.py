from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.career_profile import CareerProfile
from app.models.user import User
from app.schemas.career_profile import CareerProfileResponse, CareerProfileUpsertRequest
from app.services.security import get_current_user

router = APIRouter(prefix="/api/career-profile", tags=["career-profile"])


@router.get("/me", response_model=CareerProfileResponse | None)
def get_my_career_profile(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> CareerProfile | None:
    return db.query(CareerProfile).filter(CareerProfile.user_id == current_user.id).first()


@router.put("/me", response_model=CareerProfileResponse)
def upsert_my_career_profile(
    payload: CareerProfileUpsertRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CareerProfile:
    profile = db.query(CareerProfile).filter(CareerProfile.user_id == current_user.id).first()
    if profile is None:
        profile = CareerProfile(user_id=current_user.id)
        db.add(profile)

    for field, value in payload.model_dump().items():
        setattr(profile, field, value.strip() if isinstance(value, str) else value)

    db.commit()
    db.refresh(profile)
    return profile
