# CareerMatch Assistant

CareerMatch Assistant is a backend-focused project for managing a job search, comparing a candidate profile against job descriptions, and preparing for interviews.

The goal is not to automate job applications. The app helps the user understand each opportunity, improve application materials, and prepare for interviews while keeping the final decisions and submissions human-controlled.

## What It Does

- Stores job postings in an application tracker.
- Stores a candidate profile with skills, experience, projects, and target roles.
- Analyzes job descriptions to extract skills, seniority, and requirements.
- Compares the candidate profile against a job and explains strengths and gaps.
- Suggests CV improvements based on real experience.
- Generates interview preparation questions and study topics.
- Later, imports jobs safely from public ATS APIs such as Greenhouse and Lever.

## Why This Project Exists

Job searching can become messy quickly: job descriptions live in different places, CV tailoring is hard to track, and interview preparation is often rushed. CareerMatch Assistant turns that workflow into a structured, explainable system.

It is also designed as a learning project for backend development, API design, databases, testing, and practical AI/NLP workflows.

## Tech Stack

- Python
- FastAPI
- Pydantic
- PostgreSQL
- SQLAlchemy
- Alembic
- pytest
- Rule-based NLP first
- Optional LLM support later

## Current Status

Phase 3 is complete.

The current app includes:

- A FastAPI application.
- A `GET /health` endpoint.
- Database-backed job CRUD endpoints.
- Application tracking endpoints with statuses, notes, next actions, deadlines, and applied dates.
- SQLAlchemy job model.
- SQLAlchemy application model linked one-to-one with jobs.
- Alembic migrations for the jobs and applications tables.
- Docker Compose PostgreSQL service.
- Swagger/OpenAPI availability tests.
- Job and application endpoint tests.
- A detailed phase roadmap in `PROJECT_ROADMAP.md`.

Run the API:

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

## Safety Note

This project does not include mass auto-apply automation, LinkedIn scraping, Indeed scraping, login automation, CAPTCHA bypassing, or anything that violates job board terms.

The user reviews and submits all applications manually.
