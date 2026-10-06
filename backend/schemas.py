from datetime import datetime, date
from pydantic import BaseModel, EmailStr
from typing import Optional, List


class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserStats(BaseModel):
    xp_points: int
    level: int
    current_streak: int
    longest_streak: int
    xp_progress_in_level: int
    xp_needed_for_next: int
    level_progress_percent: float


# Skill Schemas
class SkillCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = "other"
    priority: Optional[int] = 1
    target_hours: Optional[float] = 0
    goal_date: Optional[str] = None


class SkillResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    category: Optional[str]
    priority: Optional[int]
    target_hours: Optional[float]
    total_hours_spent: Optional[float]
    goal_date: Optional[datetime]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


# Task Schemas
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    xp_reward: Optional[int] = 10
    estimated_minutes: Optional[int] = 30


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    skill_id: int
    is_completed: bool
    xp_reward: Optional[int]
    estimated_minutes: Optional[int]
    created_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


# Milestone Schemas
class MilestoneCreate(BaseModel):
    title: str
    description: Optional[str] = None
    target_date: Optional[datetime] = None
    order: Optional[int] = 0


class MilestoneResponse(BaseModel):
    id: int
    skill_id: int
    title: str
    description: Optional[str]
    target_date: Optional[datetime]
    is_completed: bool
    completed_at: Optional[datetime]
    order: int

    class Config:
        from_attributes = True


# Learning Session Schemas
class LearningSessionCreate(BaseModel):
    skill_id: Optional[int] = None
    duration_minutes: int
    notes: Optional[str] = None


class LearningSessionResponse(BaseModel):
    id: int
    skill_id: Optional[int]
    duration_minutes: int
    started_at: datetime
    ended_at: Optional[datetime]
    notes: Optional[str]

    class Config:
        from_attributes = True


# Activity Heatmap
class DailyActivityResponse(BaseModel):
    date: str
    tasks_completed: int
    minutes_spent: int
    xp_earned: int
    intensity: int


     


   

