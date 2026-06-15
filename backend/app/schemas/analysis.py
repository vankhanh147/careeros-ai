from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ResumeJobMatchRequest(BaseModel):
    resume_id: int = Field(gt=0)
    job_description_id: int = Field(gt=0)


class ScoringBreakdown(BaseModel):
    skill_score: float
    keyword_score: float
    semantic_score: float
    role_alignment_score: float = 0
    evidence_score: float = 0
    length_sanity: float
    confidence: str = "medium"
    final_score: float
    resume_role_family: str = "general software"
    jd_role_family: str = "general software"
    resume_role_signals: dict[str, list[str]] = Field(default_factory=dict)
    jd_role_signals: dict[str, list[str]] = Field(default_factory=dict)
    resume_stack_groups: list[str] = Field(default_factory=list)
    jd_stack_groups: list[str] = Field(default_factory=list)
    critical_skills: list[str] = Field(default_factory=list)
    role_alignment_notes: list[str] = Field(default_factory=list)
    evidence_notes: list[str] = Field(default_factory=list)


class PrioritizedMissingSkills(BaseModel):
    high_priority: list[str]
    medium_priority: list[str]
    low_priority: list[str]


class ResumeFeedbackItem(BaseModel):
    title: str
    message: str
    why_this_matters: str
    suggested_edit: str | None = None


class ResumeFeedback(BaseModel):
    critical_gaps: list[ResumeFeedbackItem] = Field(default_factory=list)
    cv_wording_improvements: list[ResumeFeedbackItem] = Field(default_factory=list)
    suggested_bullet_rewrites: list[ResumeFeedbackItem] = Field(default_factory=list)
    missing_evidence_areas: list[ResumeFeedbackItem] = Field(default_factory=list)
    recommended_next_edits: list[ResumeFeedbackItem] = Field(default_factory=list)


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
    resume_feedback: ResumeFeedback
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

