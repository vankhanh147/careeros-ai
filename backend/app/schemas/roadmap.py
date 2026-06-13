from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class RoadmapGenerateRequest(BaseModel):
    analysis_id: int | None = Field(default=None, gt=0)
    timeline: str | None = Field(default=None, max_length=255)


class RoadmapItem(BaseModel):
    week: str
    focus: str
    skills: list[str]
    actions: list[str]
    expected_output: str


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