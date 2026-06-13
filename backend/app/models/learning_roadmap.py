from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class LearningRoadmap(Base):
    __tablename__ = "learning_roadmaps"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    analysis_id: Mapped[int | None] = mapped_column(
        ForeignKey("match_analyses.id", ondelete="SET NULL"), index=True, nullable=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    target_role: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    timeline: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    items: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user = relationship("User", back_populates="learning_roadmaps")
    analysis = relationship("MatchAnalysis", back_populates="learning_roadmaps")