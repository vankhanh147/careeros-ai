from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RoadmapGenerateRequest(BaseModel):
    analysis_id: int | None = Field(default=None, gt=0)
    timeline: str | None = Field(default=None, max_length=255)

    @field_validator("timeline")
    @classmethod
    def optional_timeline_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class RoadmapItem(BaseModel):
    week: str
    focus: str
    skills: list[str]
    actions: list[str]
    expected_output: str
    learning_focus: str | None = None
    practice_task: str | None = None
    cv_evidence_output: str | None = None
    interview_prep: list[str] = Field(default_factory=list)
    priority: str = "medium"


class LearningRoadmapResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    analysis_id: int | None
    title: str
    target_role: str
    timeline: str
    items: list[RoadmapItem]
    summary: str
    created_at: datetime
    updated_at: datetime


RoadmapItemsRaw = list[dict[str, Any]]