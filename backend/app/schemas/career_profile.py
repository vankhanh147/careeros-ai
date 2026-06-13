from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CareerProfileUpsertRequest(BaseModel):
    target_role: str = Field(default="", max_length=255)
    current_level: str = Field(default="", max_length=100)
    skills: str = ""
    experience_summary: str = ""
    projects_summary: str = ""
    career_goal: str = ""
    timeline: str = Field(default="", max_length=255)


class CareerProfileResponse(CareerProfileUpsertRequest):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
