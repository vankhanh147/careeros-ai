from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CareerProfileUpsertRequest(BaseModel):
    target_role: str = Field(default="", max_length=255)
    current_level: str = Field(default="", max_length=100)
    skills: str = Field(default="", max_length=5000)
    experience_summary: str = Field(default="", max_length=5000)
    projects_summary: str = Field(default="", max_length=5000)
    career_goal: str = Field(default="", max_length=5000)
    timeline: str = Field(default="", max_length=255)

    @field_validator("target_role", "current_level", "skills", "experience_summary", "projects_summary", "career_goal", "timeline")
    @classmethod
    def strip_text_fields(cls, value: str) -> str:
        return value.strip()


class CareerProfileResponse(CareerProfileUpsertRequest):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime