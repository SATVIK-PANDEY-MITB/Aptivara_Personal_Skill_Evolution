from fastapi import APIRouter,Depends, HTTPException
from schemas import UserRegister, UserLogin
from sqlalchemy.orm import Session

from passlib.context import CryptContext
from database import get_db
from models import User
from jose import jwt
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/auth",tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key-change-in-production")

ALGORITHM = "HS256"



def hashed_password(password):

    return pwd_context.hash(password)

@router.post("/register")

def register(user:UserRegister,db: Session=Depends(get_db)):

    existing = db.query(User).filter(User.email==user.email).first()

    if existing:

        raise HTTPException(status_code = 400,detail="Email already regsitered")
    
    new_user = User(
        name=user.name,

        email=user.email,

        hashed_password=hashed_password(user.password)
    
    )

    db.add(new_user)

    db.commit()

    db.refresh(new_user)


    return {"message": "User registered successfully"}


@router.post("/login")


def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not pwd_context.verify(credentials.password, user.hashed_password):

        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = jwt.encode({"sub": user.email}, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": token}