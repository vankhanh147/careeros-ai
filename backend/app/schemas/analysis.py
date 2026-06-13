from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ResumeJobMatchRequest(BaseModel):
    resume_id: int = Field(gt=0)
    job_description_id: int = Field(gt=0)


class ScoringBreakdown(BaseModel):
    skill_score: float
    keyword_score: float
    semantic_score: float
    length_sanity: float
    final_score: float


class PrioritizedMissingSkills(BaseModel):
    high_priority: list[str]
    medium_priority: list[str]
    low_priority: list[str]


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
    skill_gap_summary: str
    prioritized_missing_skills: PrioritizedMissingSkills
    improvement_plan: list[str]
    created_at: datetime
    updated_at: datetime