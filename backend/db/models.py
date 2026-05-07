from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, JSON, DateTime,
    ForeignKey, UniqueConstraint, Boolean,
)
from sqlalchemy.orm import DeclarativeBase, relationship


def now_utc():
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    name = Column(String(200))
    xp = Column(Integer, default=0)
    badges = Column(JSON, default=list)
    avatar_color = Column(String(7), default="#6366f1")
    created_at = Column(DateTime(timezone=True), default=now_utc)
    last_login = Column(DateTime(timezone=True))

    roadmaps = relationship("Roadmap", back_populates="user", cascade="all, delete-orphan")
    progress = relationship("UserProgress", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    refresh_token = Column(String(512), unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=now_utc)

    user = relationship("User", back_populates="sessions")


class Roadmap(Base):
    __tablename__ = "roadmaps"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    target_role = Column(String(200), nullable=False)
    user_skills = Column(JSON, nullable=False)
    missing_skills = Column(JSON, nullable=False)
    roadmap_json = Column(JSON, nullable=False)
    months = Column(Integer, default=3)
    model_used = Column(String(100), default="nemotron-mini")
    created_at = Column(DateTime(timezone=True), default=now_utc)

    user = relationship("User", back_populates="roadmaps")
    progress = relationship("UserProgress", back_populates="roadmap", cascade="all, delete-orphan")


class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id", ondelete="CASCADE"), nullable=False)
    completed_steps = Column(JSON, default=list)
    quiz_scores = Column(JSON, default=list)
    updated_at = Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)

    user = relationship("User", back_populates="progress")
    roadmap = relationship("Roadmap", back_populates="progress")


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(Integer, primary_key=True)
    role = Column(String(200), index=True)
    question = Column(Text, nullable=False)
    difficulty = Column(String(50))
    category = Column(String(100))
    skills_tested = Column(JSON, default=list)
    answer_outline = Column(JSON, default=list)
    source = Column(String(100), default="nemotron-mini")
    hash = Column(String(64), unique=True)


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id = Column(Integer, primary_key=True)
    role = Column(String(200), index=True)
    question = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)
    correct_index = Column(Integer, nullable=False)
    skill_tag = Column(String(200))
    difficulty = Column(String(50), default="Medium")
    explanation = Column(Text)


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)
    source = Column(String(50), default="adzuna")
    role = Column(String(200), index=True)
    title = Column(String(500))
    company = Column(String(300))
    location = Column(String(300))
    description = Column(Text)
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    url = Column(String(1000))
    scraped_at = Column(DateTime(timezone=True), default=now_utc)
    hash = Column(String(64), unique=True)


class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    id = Column(Integer, primary_key=True)
    model_name = Column(String(200))
    is_finetuned = Column(Boolean, default=False)
    metrics = Column(JSON)
    samples = Column(Integer)
    created_at = Column(DateTime(timezone=True), default=now_utc)
