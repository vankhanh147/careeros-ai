from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="user", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    career_profile = relationship(
        "CareerProfile",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
    )
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    job_descriptions = relationship(
        "JobDescription", back_populates="user", cascade="all, delete-orphan"
    )
    match_analyses = relationship("MatchAnalysis", back_populates="user", cascade="all, delete-orphan")
    learning_roadmaps = relationship("LearningRoadmap", back_populates="user", cascade="all, delete-orphan")