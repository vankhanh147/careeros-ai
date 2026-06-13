from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class InterviewStartRequest(BaseModel):
    analysis_id: int | None = Field(default=None, gt=0)
    target_role: str | None = Field(default=None, max_length=255)


class InterviewAnswerRequest(BaseModel):
    answer_id: int = Field(gt=0)
    user_answer: str = Field(min_length=1)


class InterviewAnswerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: int
    question: str
    expected_keywords: list[str]
    user_answer: str | None
    score: float | None
    feedback: str | None
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