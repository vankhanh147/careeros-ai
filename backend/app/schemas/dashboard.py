from datetime import datetime

from pydantic import BaseModel


class DashboardUserInfo(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool


class DashboardLatestAnalysis(BaseModel):
    match_score: float
    skill_gap_summary: str
    created_at: datetime


class DashboardLatestRoadmap(BaseModel):
    title: str
    timeline: str
    created_at: datetime
    completed_items: int = 0
    total_items: int = 0


class DashboardLatestInterview(BaseModel):
    target_role: str
    status: str
    score: float | None
    created_at: datetime


class DashboardSummaryResponse(BaseModel):
    user: DashboardUserInfo
    has_career_profile: bool
    resume_count: int
    job_description_count: int
    latest_analysis: DashboardLatestAnalysis | None
    latest_roadmap: DashboardLatestRoadmap | None
    latest_interview: DashboardLatestInterview | None
    recommended_next_actions: list[str]
    has_new_resume_after_analysis: bool = False
    should_rerun_analysis: bool = False
    learning_loop_summary: str | None = None
