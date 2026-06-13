from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class JobDescriptionCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    company: str | None = Field(default=None, max_length=255)
    content: str = Field(min_length=1, max_length=20000)
    source_url: str | None = Field(default=None, max_length=1000)

    @field_validator("title", "content")
    @classmethod
    def required_text_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Field must not be blank")
        return stripped

    @field_validator("company", "source_url")
    @classmethod
    def optional_text_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class JobDescriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    company: str | None
    content: str
    source_url: str | None
    created_at: datetime
    updated_at: datetime