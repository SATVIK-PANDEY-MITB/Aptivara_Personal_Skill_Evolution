"""
Gamification Service - Handles XP, Levels, Streaks
"""
from datetime import datetime, date, timedelta, timezone
from sqlalchemy.orm import Session
from models import User, DailyActivity


# XP required for each level (exponential scaling)
def get_xp_for_level(level: int) -> int:
    return int(100 * (level ** 1.5))


def get_level_from_xp(xp: int) -> int:
    level = 1
    while get_xp_for_level(level + 1) <= xp:
        level += 1
    return level


def award_xp(db: Session, user: User, xp_amount: int) -> dict:
    """Award XP to user and handle level ups"""
    old_level = user.level
    user.xp_points += xp_amount
    new_level = get_level_from_xp(user.xp_points)
    
    level_up = new_level > old_level
    if level_up:
        user.level = new_level
    
    db.commit()
    
    return {
        "xp_earned": xp_amount,
        "total_xp": user.xp_points,
        "level": user.level,
        "level_up": level_up,
        "xp_for_next_level": get_xp_for_level(user.level + 1)
    }


def update_streak(db: Session, user: User) -> dict:
    """Update user's streak based on activity"""
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    if user.last_activity_date == today:
        # Already logged activity today
        return {
            "current_streak": user.current_streak,
            "longest_streak": user.longest_streak,
            "streak_maintained": True
        }
    
    if user.last_activity_date == yesterday:
        # Continuing streak
        user.current_streak += 1
    elif user.last_activity_date is None or user.last_activity_date < yesterday:
        # Streak broken or first activity
        user.current_streak = 1
    
    # Update longest streak if needed
    if user.current_streak > user.longest_streak:
        user.longest_streak = user.current_streak
    
    user.last_activity_date = today
    db.commit()
    
    return {
        "current_streak": user.current_streak,
        "longest_streak": user.longest_streak,
        "streak_maintained": True
    }


def log_daily_activity(db: Session, user: User, tasks_completed: int = 0, 
                        minutes_spent: int = 0, xp_earned: int = 0) -> DailyActivity:
    """Log or update daily activity for heatmap"""
    today = date.today()
    
    # Check if activity exists for today
    activity = db.query(DailyActivity).filter(
        DailyActivity.user_id == user.id,
        DailyActivity.date == today
    ).first()
    
    if activity:
        activity.tasks_completed += tasks_completed
        activity.minutes_spent += minutes_spent
        activity.xp_earned += xp_earned
    else:
        activity = DailyActivity(
            user_id=user.id,
            date=today,
            tasks_completed=tasks_completed,
            minutes_spent=minutes_spent,
            xp_earned=xp_earned
        )
        db.add(activity)
    
    db.commit()
    return activity


def get_activity_heatmap(db: Session, user: User, days: int = 365) -> list:
    """Get activity data for heatmap visualization"""
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    activities = db.query(DailyActivity).filter(
        DailyActivity.user_id == user.id,
        DailyActivity.date >= start_date,
        DailyActivity.date <= end_date
    ).all()
    
    # Create a dict for quick lookup
    activity_map = {a.date: a for a in activities}
    
    result = []
    current = start_date
    while current <= end_date:
        activity = activity_map.get(current)
        result.append({
            "date": current.isoformat(),
            "tasks_completed": activity.tasks_completed if activity else 0,
            "minutes_spent": activity.minutes_spent if activity else 0,
            "xp_earned": activity.xp_earned if activity else 0,
            "intensity": min(4, (activity.tasks_completed if activity else 0))  # 0-4 scale for heatmap
        })
        current += timedelta(days=1)
    
    return result


def get_user_stats(db: Session, user: User) -> dict:
    """Get comprehensive user statistics"""
    xp_for_current = get_xp_for_level(user.level)
    xp_for_next = get_xp_for_level(user.level + 1)
    xp_progress = user.xp_points - xp_for_current
    xp_needed = xp_for_next - xp_for_current
    
    return {
        "xp_points": user.xp_points,
        "level": user.level,
        "current_streak": user.current_streak,
        "longest_streak": user.longest_streak,
        "xp_progress_in_level": xp_progress,
        "xp_needed_for_next": xp_needed,
        "level_progress_percent": round((xp_progress / xp_needed) * 100, 1) if xp_needed > 0 else 100
    }
