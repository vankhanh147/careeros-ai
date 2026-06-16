from pydantic import BaseModel, Field


class FunnelUsage(BaseModel):
    registered_users: int = 0
    profile_completed_users: int = 0
    uploaded_cv_users: int = 0
    uploaded_jd_users: int = 0
    generated_analysis_users: int = 0
    generated_roadmap_users: int = 0
    started_interview_users: int = 0
    completed_interview_users: int = 0


class FeedbackTypeSummary(BaseModel):
    feedback_type: str
    total: int = 0
    useful: int = 0
    not_useful: int = 0
    useful_rate: float = 0


class CommonMissingSkill(BaseModel):
    skill: str
    count: int


class MatchHealthSummary(BaseModel):
    total_analyses: int = 0
    average_match_score: float = 0
    high_confidence_cases: int = 0
    medium_confidence_cases: int = 0
    low_confidence_cases: int = 0
    unknown_confidence_cases: int = 0


class LearningLoopSummary(BaseModel):
    users_completing_roadmap_items: int = 0
    completed_roadmap_items: int = 0
    users_rerunning_analysis_after_roadmap: int = 0


class FounderInsightsResponse(BaseModel):
    funnel: FunnelUsage
    feedback: list[FeedbackTypeSummary] = Field(default_factory=list)
    common_missing_skills: list[CommonMissingSkill] = Field(default_factory=list)
    match_health: MatchHealthSummary
    learning_loop: LearningLoopSummary
