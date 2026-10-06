from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Skill, Task, User
from auth_dependencies import get_current_user

from datetime import datetime, timedelta
from sqlalchemy import func

from ai_service import generate_learning_plan
from gamification import get_user_stats, get_activity_heatmap
from time import time




router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"]
)

# -------------------------------
# GET /dashboard/overview
# -------------------------------
@router.get("/overview")
def dashboard_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total_skills = db.query(Skill).filter(
        Skill.user_id == current_user.id
    ).count()

    total_tasks = db.query(Task).filter(
        Task.user_id == current_user.id
    ).count()

    completed_tasks = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.is_completed == True
    ).count()

    pending_tasks = total_tasks - completed_tasks

    overall_progress = 0
    if total_tasks > 0:
        overall_progress = (completed_tasks / total_tasks) * 100

    return {
        "total_skills": total_skills,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "overall_progress_percent": round(overall_progress, 2)
    }


# -------------------------------
# GET /dashboard/ai-recommendation
# -------------------------------
@router.get("/ai-recommendation")
def ai_recommendation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get user's skills and progress
    skills = db.query(Skill).filter(
        Skill.user_id == current_user.id
    ).all()
    
    skills_data = []
    for skill in skills:
        total = db.query(Task).filter(
            Task.skill_id == skill.id,
            Task.user_id == current_user.id
        ).count()
        
        completed = db.query(Task).filter(
            Task.skill_id == skill.id,
            Task.user_id == current_user.id,
            Task.is_completed == True
        ).count()
        
        progress = (completed / total * 100) if total > 0 else 0
        skills_data.append(f"- {skill.name}: {completed}/{total} tasks ({progress:.0f}%)")
    
    if not skills_data:
        return {"recommendation": "Add some skills to get AI-powered learning recommendations!"}
    
    skills_summary = "\n".join(skills_data)
    recommendation = generate_learning_plan(skills_summary)
    
    return {"recommendation": recommendation}


# -------------------------------
# GET /dashboard/user-stats (Gamification)
# -------------------------------
@router.get("/user-stats")
def user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_user_stats(db, current_user)


# -------------------------------
# GET /dashboard/activity-heatmap
# -------------------------------
@router.get("/activity-heatmap")
def activity_heatmap(
    days: int = 365,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_activity_heatmap(db, current_user, days)


# -------------------------------
# GET /dashboard/leaderboard (Top users)
# -------------------------------
@router.get("/leaderboard")
def leaderboard(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    top_users = db.query(User).order_by(User.xp_points.desc()).limit(limit).all()
    
    return [
        {
            "rank": idx + 1,
            "name": user.name,
            "level": user.level,
            "xp_points": user.xp_points,
            "current_streak": user.current_streak,
            "is_current_user": user.id == current_user.id
        }
        for idx, user in enumerate(top_users)
    ]


# -------------------------------
# GET /dashboard/weak-areas (AI Analysis)
# -------------------------------
@router.get("/weak-areas")
def weak_areas(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    skills = db.query(Skill).filter(
        Skill.user_id == current_user.id
    ).all()
    
    weak_skills = []
    for skill in skills:
        total = db.query(Task).filter(
            Task.skill_id == skill.id,
            Task.user_id == current_user.id
        ).count()
        
        completed = db.query(Task).filter(
            Task.skill_id == skill.id,
            Task.user_id == current_user.id,
            Task.is_completed == True
        ).count()
        
        if total > 0:
            progress = (completed / total) * 100
            if progress < 50:  # Less than 50% completion = weak area
                weak_skills.append({
                    "skill_id": skill.id,
                    "skill_name": skill.name,
                    "category": skill.category,
                    "progress_percent": round(progress, 1),
                    "pending_tasks": total - completed,
                    "recommendation": f"Focus on completing {total - completed} remaining tasks in {skill.name}"
                })
    
    # Sort by lowest progress first
    weak_skills.sort(key=lambda x: x["progress_percent"])
    
    return weak_skills


# -------------------------------
# GET /dashboard/skills-progress
# -------------------------------
@router.get("/skills-progress")
def skills_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    skills = db.query(Skill).filter(
        Skill.user_id == current_user.id
    ).all()

    result = []

    for skill in skills:
        total_tasks = db.query(Task).filter(
            Task.skill_id == skill.id,
            Task.user_id == current_user.id
        ).count()

        completed_tasks = db.query(Task).filter(
            Task.skill_id == skill.id,
            Task.user_id == current_user.id,
            Task.is_completed == True
        ).count()

        progress = 0
        if total_tasks > 0:
            progress = (completed_tasks / total_tasks) * 100

        result.append({
            "skill_id": skill.id,
            "skill_name": skill.name,
            "progress_percent": round(progress, 2)
        })

    return result


# -------------------------------
# GET /dashboard/recent-tasks
# -------------------------------
@router.get("/recent-tasks")
def recent_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tasks = db.query(Task).filter(
        Task.user_id == current_user.id
    ).order_by(Task.created_at.desc()).limit(5).all()

    return [
        {
            "task_id": task.id,
            "title": task.title,
            "skill_id": task.skill_id,
            "is_completed": task.is_completed
        }
        for task in tasks
    ]


# -------------------------------
# GET /dashboard/skills-summary
# -------------------------------
@router.get("/skills-summary")
def skills_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    skills = db.query(Skill).filter(
        Skill.user_id == current_user.id
    ).all()

    completed = 0
    in_progress = 0

    for skill in skills:
        total = db.query(Task).filter(
            Task.skill_id == skill.id,
            Task.user_id == current_user.id
        ).count()

        done = db.query(Task).filter(
            Task.skill_id == skill.id,
            Task.user_id == current_user.id,
            Task.is_completed == True
        ).count()

        if total > 0 and total == done:
            completed += 1
        else:
            in_progress += 1

    return {
        "completed_skills": completed,
        "in_progress_skills": in_progress
    }


# Weekly task anlytics

@router.get("/weekly-progress")
def weekly_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    today = datetime.utcnow().date()
    start_date = today - timedelta(days=6)

    data = (db.query(
        func.date(Task.created_at).label('date'),
        func.count(Task.id).label('count')
    ).filter(
        Task.user_id == current_user.id,
        Task.created_at >= start_date
    ).group_by(
        func.date(Task.created_at)
    ).all()
    )
  
    result=[]

    for i in range(7):

        date = start_date + timedelta(days=i)
        for record in data:
            if record.date == date:
                count = record.count
                break
        result.append({"date": date.isoformat(), "task_count": count})

    return result


# Monthly completion analytics


@router.get("/monthly-progress")

def monthly_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    today = datetime.utcnow().date()
    start_date = today - timedelta(days=29) #last 30 days

    data = (
        db.query(
        func.date(Task.created_at).label('date'),
        func.count(Task.id).label('count')
    ).filter(
        Task.user_id == current_user.id,
        Task.created_at >= start_date
    ).group_by(
        func.date(Task.created_at)).all()
    ).all()
    
  
    result=[]

    for i in range(30):

        day = start_date + timedelta(days=i)
        count = next((d.count for d in data if d.date == day), 0)
        result.append({"date": day.isoformat(), "tasks": count})
    return result


# Task Completion Trend(Last 7 days)

@router.get("/task-trend")
def task_trend(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    today = datetime.utcnow()
    data = []

    for i in range(6,-1,-1): 
        day= today - timedelta(days=i)
        start=day.replace(hour=0,minute=0,second=0,microsecond=0)
        end=start + timedelta(days=1)


        completed = db.query(Task).filter(
            Task.user_id == current_user.id,
            Task.is_completed == True,
            Task.created_at >= start,
            Task.created_at < end
        ).count()

        data.append({
            "date": start.strftime("%Y-%m-%d"),
            "completed_tasks": completed

        })

        return data
    
    # Skill Progress Chart API

@router.get("/skills-chart")
def skills_chart(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
        skills = db.query(Skill).filter(
            Skill.user_id == current_user.id
        ).all()

        chart_data = []

        for skill in skills:
            total = db.query(Task).filter(
                Task.skill_id == skill.id,
                Task.user_id == current_user.id
            ).count()

            completed = db.query(Task).filter(
                Task.skill_id == skill.id,
                Task.user_id == current_user.id,
                Task.is_completed == True
            ).count()

            percent=(completed/total*100) if total>0 else 0

            chart_data.append({
                "skill": skill.name,
                "progress":round(percent,2)
            })

            return chart_data
        
# AI Skill Recommendations

@router.get("/recommendations")
def skill_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    skills = db.query(Skill).filter(Skill.user_id == current_user.id).all()
    recommendations = []

    for skill in skills:
        total = db.query(Task).filter(
            Task.skill_id == skill.id,
            Task.user_id == current_user.id
        ).count()

        completed = db.query(Task).filter(
            Task.skill_id == skill.id,
            Task.user_id == current_user.id,
            Task.is_completed == True
        ).count()

        if total == 0:
            recommendations.append({
                "skill": skill.name,
                "advice": "Add tasks to start progress"
            })
        elif completed / total < 0.4:
            recommendations.append({
                "skill": skill.name,
                "advice": "Low progress – focus more this week"
            })

    return recommendations

    
#Priority Recommendations

@router.get("/priority-recommendations")
def priority_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    skills = db.query(Skill).filter(
        Skill.user_id == current_user.id
    ).all()

    result=[]

    for skill in skills:
        total = db.query(Task).filter(
            Task.skill_id == skill.id,
            Task.user_id == current_user.id,
        ).count()

        completed = db.query(Task).filter(
            Task.skill_id == skill.id,
            Task.user_id == current_user.id,
            Task.is_completed == True
        ).count()

        pending = total - completed
        progress=(completed/total) if total>0 else 0
        priority_score = pending * (1 - progress)

        result.append({
            "skill": skill.name,
            "pending_tasks": pending,
            "progress_percent": round(progress*100, 2),
            "priority_score": (priority_score,2)
        })

    result.sort(key=lambda x: x["priority_score"], reverse=True)

    return result

#Deadline-Aware AI Advice

@router.get("/deadline-alerts")
def deadline_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    today=datetime.utcnow()
    alerts=[]

    skills = db.query(Skill).filter(
        Skill.user_id == current_user.id,
        Skill.goal_date!= None
    ).all()


    for skill in skills:
        days_left = (skill.goal_date - today).days

        total = db.query(Task).filter(
            Task.skill_id == skill.id,
            Task.user_id == current_user.id,
        ).count()

        completed = db.query(Task).filter(
            Task.skill_id == skill.id,
            Task.user_id == current_user.id,
            Task.is_completed == True
        ).count()


        progress = (completed / total*100) if total > 0 else 0


        if days_left <= 7 and progress < 50:
            alerts.append({
                "skill": skill.name,
                "days_left": days_left,
                "progress": round(progress, 2),
                "alert": "Deadline approaching with low progress!"
            })

    return alerts


#GPT-Powered Learning Plan

@router.get("/learning-plan")
def learning_plan(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    skills = db.query(Skill).filter(
        Skill.user_id == current_user.id
    ).all()

    plan=[]

    for skill in skills:
        total = db.query(Task).filter(
            Task.skill_id == skill.id,
            Task.user_id == current_user.id,
        ).count()

        completed = db.query(Task).filter(
            Task.skill_id == skill.id,
            Task.user_id == current_user.id,
            Task.is_completed == True
        ).count()

        progress=(completed/total*100) if total>0 else 0

        if progress <30:
            advice="Focus on fundamentals and daily practice"
        elif progress<70:
            advice="Increase difficulty and diversify tasks"
        else:
            advice="Revise & apply knowledge in projects"

            plan.append({
                "skill": skill.name,
                "progress": round(progress,2),
                "learning_advice": advice
            })

    return plan

#AI-Learning Plan

@router.get("/ai-learning-plan")

def ai_learning_plan(

    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    skills=db.query(Skill).filter(Skill.user_id==current_user.id).all()

    skill_data=[

        {
            "skill": s.name,
            "progress": s.progress_percent}
            for s in skills
    ]


    plan=generate_learning_plan(skill_data)

    return{"plan":plan}

#Productivity Score


@router.get("/productivity-score")
def productivity_score(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total = db.query(Task).filter(
        Task.user_id == current_user.id
    ).count()

    completed = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.is_completed == True
    ).count()

    score=int((completed/total*100) if total>0 else 0)

    return {

        "score": score,

        "level": (

            "🔥 Excellent" if score >= 80 else
            "🙂 Average" if score >= 50 else
            "⚠ Needs Focus"

        )
    }

# Calendar Integration

@router.get("/calendar")
def calendar_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tasks = db.query(Task).filter(
        Task.user_id == current_user.id
    ).all()

    return [
        {
            "title":t.title,
            "date": t.deadline
        }

        for t in tasks if t.deadline
    ]

#Gamification Badges
AI_RATE_LIMIT = {}  # user_id -> last_called_timestamp
AI_COOLDOWN = 60    # seconds


@router.get("/badges")
def badges(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    completed = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.is_completed == True
    ).count()

    badges = []

    if completed >= 10:
        badges.append("🥉 Beginner Achiever")
    if completed >= 30:
        badges.append("🥈 Consistency Master")
    if completed >= 60:
        badges.append("🥇 Productivity Beast")

    return badges


#Simple Rate Limit
@router.get("/ai-learning-plan")
def ai_learning_plan(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    now=time()

    last_called=AI_RATE_LIMIT.get(current_user.id,0)

    if now-last_called<AI_COOLDOWN:

        return{
            "plan":"⏳ Please wait before requesting another AI learning plan."
        }
    
    AI_RATE_LIMIT[current_user.id]=now
    skills = db.query(Skill).filter(

        Skill.user_id==current_user.id
    )

    skill_data=[

        {
            "skill":s.name,"progress":s.progress_percent}
            for s in skills
        
    ]

    plan=generate_learning_plan(skill_data)

    return {"plan":plan}
