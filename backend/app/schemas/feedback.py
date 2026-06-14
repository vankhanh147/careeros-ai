from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


FeedbackType = Literal["analysis", "roadmap", "interview"]


class FeedbackCreateRequest(BaseModel):
    feedback_type: FeedbackType
    useful: bool
    comment: str | None = Field(default=None, max_length=2000)

    @field_validator("comment")
    @classmethod
    def optional_comment_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class FeedbackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    feedback_type: str
    useful: bool
    comment: str | None
    created_at: datetime
