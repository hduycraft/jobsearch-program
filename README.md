# CareerMatch Assistant

CareerMatch Assistant is a human-in-the-loop job-search and interview-preparation assistant built with FastAPI.

It helps a candidate keep job opportunities organized, compare their profile against job descriptions, identify skill gaps, and prepare better application materials and interview practice.

## What It Does

- Tracks jobs and application progress.
- Stores a candidate profile with skills, experience, projects, and target roles.
- Analyzes job descriptions for skills, seniority, and requirements.
- Scores how well a profile matches a job.
- Suggests honest CV improvements based on real experience.
- Generates interview preparation questions and study topics.
- Later, imports jobs from safe public ATS APIs such as Greenhouse and Lever.

## Current Status

Phase 4 is complete.

The app currently includes:

- A FastAPI backend.
- `GET /health`
- Database-backed job CRUD endpoints under `/jobs`
- Application tracking endpoints under `/applications`
- Profile management endpoints under `/profiles`
- SQLAlchemy ORM model for jobs.
- SQLAlchemy ORM model for applications with a one-to-one job relationship.
- SQLAlchemy ORM model for candidate profiles.
- Alembic migrations for the `jobs`, `applications`, and `profiles` tables.
- PostgreSQL configuration via `DATABASE_URL`.
- Docker Compose service for local PostgreSQL.
- Swagger/OpenAPI availability tests.
- Job, application, and profile endpoint tests.
- A detailed build plan in [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md).

## Tech Stack

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- PostgreSQL
- pytest
- Rule-based NLP first, optional LLM support later

## Run Locally

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Start PostgreSQL:

```powershell
docker compose up -d postgres
```

Apply database migrations:

```powershell
.\.venv\Scripts\alembic.exe upgrade head
```

Run tests:

```powershell
python -m pytest
```

Start the API:

```powershell
uvicorn app.main:app --reload
```

Open:

```text
http://localhost:8000/health
```

Expected response:

```json
{
  "status": "ok"
}
```

API docs:

```text
http://localhost:8000/docs
```

## Safety Note

This project does not include mass auto-apply automation, LinkedIn scraping, Indeed scraping, login automation, CAPTCHA bypassing, or workflows that violate job board terms.

The user reviews all suggestions and submits applications manually.

## Project Docs

- [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md): detailed phase plan and future-session handoff.
- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md): short project overview.
