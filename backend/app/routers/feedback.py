from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.user_feedback import UserFeedback
from app.schemas.feedback import FeedbackCreateRequest, FeedbackResponse
from app.services.security import get_current_user
from app.services.usage_tracking import EVENT_FEEDBACK_SUBMITTED, add_usage_event

router = APIRouter(prefix="/api/feedback", tags=["feedback"])


@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def create_feedback(
    payload: FeedbackCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserFeedback:
    feedback = UserFeedback(
        user_id=current_user.id,
        feedback_type=payload.feedback_type,
        useful=payload.useful,
        comment=payload.comment,
    )
    db.add(feedback)
    add_usage_event(
        db,
        user_id=current_user.id,
        event_type=EVENT_FEEDBACK_SUBMITTED,
        metadata={"feedback_type": payload.feedback_type, "useful": payload.useful},
    )
    db.commit()
    db.refresh(feedback)
    return feedback
