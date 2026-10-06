# Aptivara — Personal Skill Evolution Platform

Aptivara is a full-stack application for turning personal learning into a measurable, game-like workflow. Users can create skills, schedule tasks, earn XP, maintain daily streaks, analyze their progress, and receive AI-generated seven-day learning recommendations.

<div align="center">

![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-59666C?logo=sqlalchemy&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Local-003B57?logo=sqlite&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT-4o-mini-412991?logo=openai&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

</div>

## Project at a Glance

| Metric | Current implementation |
| --- | ---: |
| Frontend | React 18 + Vite |
| Backend | FastAPI |
| Database | SQLite with SQLAlchemy |
| Authentication | JWT using Python-JOSE and bcrypt |
| AI provider | OpenAI Chat Completions |
| Frontend pages | 3 routes |
| Backend API routers | 4 |
| Skill categories | 9 |
| Database entities | 6 primary entities |
| Default development ports | Frontend `5173`, backend `8000` |
| Build system | Vite production build |

> The project is a learning-oriented MVP. It includes complete user, skill, task, gamification, analytics, and AI recommendation flows; it does not currently provide automated tests, containerization, or production deployment configuration.

## Features

### Core learning workflow

- Create and manage personal skills with description, category, priority, target hours, and goal date.
- Add tasks under each skill and assign XP and estimated work time.
- Complete tasks to earn XP, unlock levels, and update daily streaks.
- View the overall completion percentage across all activities.
- Track the latest five tasks and per-skill progress.

### Gamification

- XP-based progression with level thresholds calculated from accumulated points.
- Level progression with progress toward the next level.
- Current streak and longest streak tracking.
- Weekly and monthly task analytics.
- Leaderboard sorted by XP and level.

### Analytics and insights

- 90-day activity heatmap with zero to four intensity levels.
- Seven-day completion trend.
- Thirty-day task distribution.
- Completed-versus-in-progress skill summary.
- Skills that are below 50% complete, with actionable recommendations.
- Personal dashboard overview and detailed skill progress.

### AI coaching

- Generates a seven-day learning plan from the user's skills and task completion data.
- Uses the OpenAI API through the configured `OPENAI_API_KEY`.
- Falls back to a simple productivity message when the AI service fails.

### User experience

- Responsive dashboard with overview, skills, focus, analytics, and AI tabs.
- JWT-protected routes.
- Focus timer with preset durations of 25, 45, and 60 minutes.
- Local token storage for the browser session.
- Notifications for completed tasks, level-ups, and focus sessions.

## Technology Stack

### Frontend

- React 18
- React Router DOM 6
- Vite 5
- JavaScript ES modules

### Backend

- Python 3.10+
- FastAPI 0.109+
- SQLAlchemy 2.0+
- SQLite 3
- Pydantic 2
- Python-JOSE with JWT
- Passlib and bcrypt
- Python-dotenv
- OpenAI Python SDK

## Architecture

```text
Browser
  |
  v
React + Vite
  |
  | HTTP/JSON + JWT
  v
FastAPI REST API
  |
  +-- Auth router
  +-- Skills router
  +-- Tasks router
  +-- Dashboard router
  |
  v
SQLAlchemy models
  |
  v
SQLite database (skill_tracker.db)
```

The application has a single FastAPI service and one React client. Data is persisted locally in the repository-root SQLite database unless the database path is changed.

## Project Structure

```text
Aptivara-Your-Personal-Skill-Evolution-main/
├── backend/
│   ├── ai_service.py          # OpenAI-powered learning-plan generation
│   ├── auth.py                # Registration and login endpoints
│   ├── auth_dependencies.py   # JWT authentication dependency
│   ├── auth_utils.py          # Authentication utilities
│   ├── dashboard.py           # Analytics and leaderboard endpoints
│   ├── database.py            # SQLAlchemy engine and session setup
│   ├── gamification.py        # XP, levels, streaks, and activity records
│   ├── main.py                # FastAPI application and router registration
│   ├── models.py              # SQLAlchemy database models
│   ├── requirements.txt       # Backend dependencies
│   ├── schemas.py             # Pydantic request and response models
│   ├── skills.py              # Skill CRUD endpoints
│   ├── tasks.py               # Task creation and completion endpoints
│   └── skill_tracker.db       # Local SQLite database
├── frontend/
│   ├── package.json           # Frontend dependencies and scripts
│   ├── vite.config.js         # Vite configuration
│   └── src/
│       ├── components/
│       └── pages/
└── README.md
```

## Getting Started

### 1. Prerequisites

Install:

- Python 3.10 or newer
- Node.js 18 or newer
- npm
- Git
- A modern browser

### 2. Clone and enter the project

```bash
git clone <repository-url>
cd Aptivara-Your-Personal-Skill-Evolution-main
```

### 3. Configure the backend

```bash
cd backend
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Windows Command Prompt
# .venv\Scripts\activate.bat

python -m pip install --upgrade pip
pip install -r requirements.txt
```

Create a `.env` file inside the `backend/` directory:

```env
SECRET_KEY=replace-with-a-long-random-secret
OPENAI_API_KEY=replace-with-your-openai-api-key
```

### 4. Start the backend

From the project root:

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Expected startup output includes:

```text
Application startup complete.
Uvicorn running on http://127.0.0.1:8000
```

Open the interactive API documentation at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 5. Start the frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

The Vite development server normally runs at:

```text
http://localhost:5173
```

### 6. Register and use the application

1. Open `http://localhost:5173`.
2. Select **Register**.
3. Create an account using a valid email and password.
4. Sign in with the new credentials.
5. Add skills, configure tasks, complete work, and monitor the dashboard.

## API Reference

All protected endpoints require an `Authorization: Bearer <token>` header.

### Authentication

| Method | Endpoint | Description | Authentication |
| --- | --- | --- | --- |
| `POST` | `/auth/register` | Create a user account | No |
| `POST` | `/auth/login` | Authenticate and return a JWT | No |

Example registration:

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Aptivara User",
    "email": "user@example.com",
    "password": "secure-password"
  }'
```

Example login:

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secure-password"
  }'
```

### Skills

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/skills/` | Create a skill |
| `GET` | `/skills/` | List skills for the authenticated user |
| `PUT` | `/skills/{skill_id}` | Update a skill |
| `DELETE` | `/skills/{skill_id}` | Delete a skill |

### Tasks

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/tasks/{skill_id}` | Create a task for a skill |
| `GET` | `/tasks/{skill_id}` | List tasks for a skill |
| `PUT` | `/tasks/{task_id}/complete` | Mark a task complete and award XP |

### Dashboard

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/dashboard/overview` | Total skills, tasks, completed tasks, and progress |
| `GET` | `/dashboard/user-stats` | XP, level, streak, and level-progress data |
| `GET` | `/dashboard/activity-heatmap?days=90` | Activity data for the heatmap |
| `GET` | `/dashboard/leaderboard?limit=10` | Top users by XP |
| `GET` | `/dashboard/weak-areas` | Skills below 50% completion |
| `GET` | `/dashboard/ai-recommendation` | AI-generated seven-day learning plan |
| `GET` | `/dashboard/skills-progress` | Per-skill completion percentage |
| `GET` | `/dashboard/recent-tasks` | Most recent five tasks |
| `GET` | `/dashboard/skills-summary` | Completed and in-progress skill counts |
| `GET` | `/dashboard/weekly-progress` | Seven-day task-count trend |
| `GET` | `/dashboard/monthly-progress` | Thirty-day task-count trend |
| `GET` | `/dashboard/task-trend` | Seven-day completion trend |
| `GET` | `/dashboard/skills-chart` | Skill chart data |

Example authenticated request:

```bash
curl -H "Authorization: Bearer <access_token>" \
  http://localhost:8000/dashboard/overview
```

## Database Models

| Model | Purpose |
| --- | --- |
| `User` | Account, XP, level, streak, and relationships |
| `Skill` | Learning goal with category, priority, target hours, and milestones |
| `Task` | Actionable learning item with XP and time estimates |
| `Milestone` | Skill checkpoint with completion date and order |
| `DailyActivity` | Daily task, minute, and XP totals for analytics |
| `LearningSession` | Focus and Pomodoro session metadata |

The database schema is initialized automatically when the FastAPI application starts because `Base.metadata.create_all(bind=engine)` is executed in the application module.

## Current Limitations and Technical Debt

The current codebase is functional for local development, but several production-readiness items should be addressed before deployment:

1. Replace the fallback JWT secret with a required environment variable.
2. Add password-strength validation and account-lockout controls.
3. Add automated tests for authentication, authorization, gamification, and dashboard endpoints.
4. Validate or normalize the OpenAI API key before startup.
5. Add environment-specific configuration instead of hard-coded development URLs.
6. Add request-rate limiting and structured API logging.
7. Add database migrations instead of relying on dynamic table creation.
8. Add input validation and authorization checks for all user-owned resources.
9. Add Docker and CI/CD configuration.
10. Replace local storage with a secure cookie or server-managed session model if browser session security is required.

## Development Commands

```bash
# Backend
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run build
npm run dev -- --host 0.0.0.0
```

## Production Considerations

- Set `SECRET_KEY` to a securely generated value and do not commit it to source control.
- Use a production-grade database such as PostgreSQL.
- Store the OpenAI key in a secure secret manager.
- Use HTTPS and configure trusted frontend origins in CORS.
- Run the application behind a reverse proxy such as Nginx.
- Add monitoring, health checks, backups, and database migrations.
- Use a non-root container user and do not expose the SQLite database directly.
- Add rate limiting, audit logging, and basic security headers.

## Configuration

| Variable | Required | Description |
| --- | --- | --- |
| `SECRET_KEY` | Yes | Secret used to sign and verify JWT tokens |
| `OPENAI_API_KEY` | Yes for AI recommendations | OpenAI API credential |

The backend loads environment variables using `python-dotenv`.

## License

This project is licensed under the MIT License. See the repository's license file for details if one is included in the project distribution.

## Contributing

1. Create a feature branch.
2. Make focused changes with clear commit messages.
3. Run the frontend build and backend validation relevant to your change.
4. Add tests for new behavior.
5. Open a pull request with a summary, screenshots where useful, and verification steps.

## Support

For local development problems, check the backend terminal for FastAPI errors, confirm both ports are available, and review the browser developer console for failed API requests.
