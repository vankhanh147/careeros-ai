from pydantic import BaseModel


class UsageSummaryResponse(BaseModel):
    total_resume_uploads: int
    total_analysis: int
    total_roadmaps: int
    total_interviews: int
    total_feedback: int
