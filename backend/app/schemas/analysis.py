from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ResumeJobMatchRequest(BaseModel):
    resume_id: int = Field(gt=0)
    job_description_id: int = Field(gt=0)


class ScoringBreakdown(BaseModel):
    skill_score: float
    keyword_score: float
    length_score: float
    final_score: float


class MatchAnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    resume_id: int
    job_description_id: int
    match_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    keyword_overlap: list[str]
    summary: str
    suggestions: list[str]
    resume_text_preview: str
    jd_text_preview: str
    resume_detected_skills: list[str]
    jd_detected_skills: list[str]
    scoring_breakdown: ScoringBreakdown
    created_at: datetime
    updated_at: datetime