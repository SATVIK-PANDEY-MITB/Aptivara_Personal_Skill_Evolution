from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from database import get_db
from models import Task, User
from schemas import TaskCreate, TaskResponse
from auth_dependencies import get_current_user
from gamification import award_xp, update_streak, log_daily_activity

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/{skill_id}", response_model=TaskResponse)
def create_task(
    skill_id: int,
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_task = Task(
        title=task.title,
        skill_id=skill_id,
        user_id=current_user.id,
        xp_reward=task.xp_reward if hasattr(task, 'xp_reward') else 10,
        estimated_minutes=task.estimated_minutes if hasattr(task, 'estimated_minutes') else 30
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


@router.get("/{skill_id}", response_model=list[TaskResponse])
def get_tasks(
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Task).filter(
        Task.skill_id == skill_id,
        Task.user_id == current_user.id
    ).all()


@router.put("/{task_id}/complete")
def complete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()

    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if db_task.is_completed:
        return {"message": "Task already completed"}

    # Mark as completed
    db_task.is_completed = True
    db_task.completed_at = datetime.now(timezone.utc)
    db.commit()

    # Award XP
    xp_result = award_xp(db, current_user, db_task.xp_reward)
    
    # Update streak
    streak_result = update_streak(db, current_user)
    
    # Log daily activity
    log_daily_activity(
        db, current_user,
        tasks_completed=1,
        minutes_spent=db_task.estimated_minutes,
        xp_earned=db_task.xp_reward
    )

    return {
        "message": "Task completed!",
        "xp_earned": xp_result["xp_earned"],
        "total_xp": xp_result["total_xp"],
        "level": xp_result["level"],
        "level_up": xp_result["level_up"],
        "current_streak": streak_result["current_streak"]
    }

    return {"message":"Task completed"}

