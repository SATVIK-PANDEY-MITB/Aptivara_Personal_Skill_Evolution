from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth import router as auth_router
from skills import router as skills_router
from tasks import router as tasks_router
from dashboard import router as dashboard_router
from database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Skill Tracker API")

# CORS - Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(skills_router)
app.include_router(tasks_router)
app.include_router(dashboard_router)


@app.get("/")
def root():
    return {"message": "Skill Tracker API is running"}