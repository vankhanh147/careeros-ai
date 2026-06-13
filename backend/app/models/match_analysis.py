from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class MatchAnalysis(Base):
    __tablename__ = "match_analyses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id", ondelete="CASCADE"), index=True, nullable=False)
    job_description_id: Mapped[int] = mapped_column(
        ForeignKey("job_descriptions.id", ondelete="CASCADE"), index=True, nullable=False
    )
    match_score: Mapped[float] = mapped_column(Float, nullable=False)
    matched_skills: Mapped[str] = mapped_column(Text, nullable=False)
    missing_skills: Mapped[str] = mapped_column(Text, nullable=False)
    keyword_overlap: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    suggestions: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user = relationship("User", back_populates="match_analyses")
    resume = relationship("Resume", back_populates="match_analyses")
    job_description = relationship("JobDescription", back_populates="match_analyses")