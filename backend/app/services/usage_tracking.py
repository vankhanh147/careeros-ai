import json
import logging
from typing import Any

from sqlalchemy.orm import Session

from app.models.usage_event import UsageEvent

logger = logging.getLogger("careeros_api.usage_tracking")

EVENT_RESUME_UPLOADED = "resume_uploaded"
EVENT_JD_UPLOADED = "jd_uploaded"
EVENT_ANALYSIS_GENERATED = "analysis_generated"
EVENT_ROADMAP_GENERATED = "roadmap_generated"
EVENT_INTERVIEW_STARTED = "interview_started"
EVENT_INTERVIEW_COMPLETED = "interview_completed"
EVENT_FEEDBACK_SUBMITTED = "feedback_submitted"

TRACKED_EVENTS = {
    EVENT_RESUME_UPLOADED,
    EVENT_JD_UPLOADED,
    EVENT_ANALYSIS_GENERATED,
    EVENT_ROADMAP_GENERATED,
    EVENT_INTERVIEW_STARTED,
    EVENT_INTERVIEW_COMPLETED,
    EVENT_FEEDBACK_SUBMITTED,
}


def add_usage_event(db: Session, *, user_id: int, event_type: str, metadata: dict[str, Any] | None = None) -> UsageEvent:
    event = UsageEvent(
        user_id=user_id,
        event_type=event_type,
        metadata_json=json.dumps(metadata, ensure_ascii=False) if metadata else None,
    )
    db.add(event)
    return event


def track_usage_event(db: Session, *, user_id: int, event_type: str, metadata: dict[str, Any] | None = None) -> None:
    if event_type not in TRACKED_EVENTS:
        logger.warning("Skipped unknown usage event", extra={"user_id": user_id, "event_type": event_type})
        return
    try:
        add_usage_event(db, user_id=user_id, event_type=event_type, metadata=metadata)
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Could not track usage event", extra={"user_id": user_id, "event_type": event_type})
