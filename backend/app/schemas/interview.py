from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class InterviewStartRequest(BaseModel):
    analysis_id: int | None = Field(default=None, gt=0)
    target_role: str | None = Field(default=None, max_length=255)

    @field_validator("target_role")
    @classmethod
    def optional_target_role_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class InterviewAnswerRequest(BaseModel):
    answer_id: int = Field(gt=0)
    user_answer: str = Field(min_length=1, max_length=5000)

    @field_validator("user_answer")
    @classmethod
    def answer_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Answer must not be blank")
        return stripped


class InterviewAnswerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: int
    question: str
    expected_keywords: list[str]
    question_reason: str | None = None
    related_skills: list[str] = Field(default_factory=list)
    question_category: str | None = None
    better_answer_hint: str | None = None
    user_answer: str | None
    score: float | None
    feedback: str | None
    feedback_category: str | None = None
    created_at: datetime


class InterviewSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    analysis_id: int | None
    target_role: str
    status: str
    score: float | None
    summary: str | None
    answers: list[InterviewAnswerResponse]
    created_at: datetime
    updated_at: datetime