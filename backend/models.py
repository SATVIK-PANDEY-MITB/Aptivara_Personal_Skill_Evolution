from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Boolean, Float, Date
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, timezone


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # Gamification
    xp_points = Column(Integer, default=0)
    level = Column(Integer, default=1)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_activity_date = Column(Date, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    skills = relationship("Skill", back_populates="user", cascade="all, delete-orphan")
    activities = relationship("DailyActivity", back_populates="user", cascade="all, delete-orphan")
    learning_sessions = relationship("LearningSession", back_populates="user", cascade="all, delete-orphan")


# Skill Categories
SKILL_CATEGORIES = [
    "programming", "languages", "fitness", "music", 
    "design", "business", "science", "personal", "other"
]


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String, default="other")
    priority = Column(Integer, default=1)  # 1=Low, 2=Medium, 3=High
    target_hours = Column(Float, default=0)  # Target learning hours
    total_hours_spent = Column(Float, default=0)
    goal_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="skills")
    tasks = relationship("Task", back_populates="skill", cascade="all, delete-orphan")
    milestones = relationship("Milestone", back_populates="skill", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    is_completed = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    skill_id = Column(Integer, ForeignKey("skills.id"))
    xp_reward = Column(Integer, default=10)  # XP earned on completion
    estimated_minutes = Column(Integer, default=30)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True), nullable=True)

    skill = relationship("Skill", back_populates="tasks")


class Milestone(Base):
    """Major checkpoints within a skill"""
    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id"))
    title = Column(String, nullable=False)
    description = Column(Text)
    target_date = Column(DateTime(timezone=True))
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    skill = relationship("Skill", back_populates="milestones")


class DailyActivity(Base):
    """Tracks daily activity for heatmap"""
    __tablename__ = "daily_activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date, nullable=False)
    tasks_completed = Column(Integer, default=0)
    minutes_spent = Column(Integer, default=0)
    xp_earned = Column(Integer, default=0)

    user = relationship("User", back_populates="activities")


class LearningSession(Base):
    """Focus/Pomodoro sessions"""
    __tablename__ = "learning_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=True)
    duration_minutes = Column(Integer, nullable=False)
    started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    ended_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text)

    user = relationship("User", back_populates="learning_sessions")








