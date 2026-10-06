from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone

from database import get_db
from models import Skill, User, Task
from schemas import SkillCreate, SkillResponse
from auth_dependencies import get_current_user

router = APIRouter(prefix="/skills", tags=["skills"])


@router.post("/", response_model=SkillResponse)
def create_skill(
    skill: SkillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_skill = Skill(
        name=skill.name,
        description=skill.description,
        category=skill.category or "other",
        priority=skill.priority or 1,
        target_hours=skill.target_hours or 0,
        goal_date=datetime.combine(
            datetime.strptime(skill.goal_date, "%Y-%m-%d").date(),
            datetime.min.time(),
            tzinfo=timezone.utc
        ) if skill.goal_date else None,
        user_id=current_user.id
    )

    db.add(new_skill)
    db.commit()
    db.refresh(new_skill)
    return new_skill


@router.get("/", response_model=List[SkillResponse])
def read_skills(

    db:Session=Depends(get_db),

    current_user:User = Depends(get_current_user)
):
    


    return db.query(Skill).filter(Skill.user_id == current_user.id).all()



@router.put("/{skill_id}",response_model=SkillResponse)

def update_skill(

    skill_id: int,

    skill: SkillCreate,

    db:Session=Depends(get_db),

    current_user : User = Depends(get_current_user)
):
    


    db_skill = db.query(Skill).filter(

        Skill.id == skill_id,

        Skill.user_id == current_user.id
    ).first()


    if not db_skill:

        raise HTTPException(status_code=404,detail="Skill not found")
    
    for k,v in skill.model_dump().items():


        setattr(db_skill,k,v)



    db.commit()

    db.refresh(db_skill)

    return db_skill
    



@router.delete("/{skill_id}")

def delete_skill(

    skill_id: int,

    db:Session =Depends(get_db),

    current_user:User = Depends(get_current_user)
):
    

    db_skill = db.query(Skill).filter(

        Skill.id == skill_id,

        Skill.user_id == current_user.id
    ).first()


    if not db_skill:


            raise HTTPException(status_code=404,detail="Skill not found")
        

    db.delete(db_skill)

    db.commit()


    return {"message":"Skill deleted"}


