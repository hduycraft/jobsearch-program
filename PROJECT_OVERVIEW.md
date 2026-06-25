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
- Stores generated CV, cover letter, and interview prep outputs for later review.
- Imports manually collected jobs in bulk.
- Indexes jobs for local semantic-style search and retrieves relevant profile context.

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
- Optional local LLM support through Ollama
- Local deterministic embedding/search foundation

## Current Status

Phase 12 is complete.

The current app includes:

- A FastAPI application.
- A `GET /health` endpoint.
- Database-backed job CRUD endpoints.
- Application tracking endpoints with statuses, notes, next actions, deadlines, and applied dates.
- Profile management endpoints for target roles, skills, experience summary, and projects.
- Job description analysis endpoint for skills, seniority, and requirement summaries.
- Match scoring endpoint for explainable profile-to-job fit.
- CV tailoring suggestion endpoint.
- Interview prep endpoint.
- Optional LLM provider interface with `none`, `fake`, and local `ollama` providers.
- Generated asset endpoints for saving and listing generated outputs per job.
- Manual bulk job import endpoint.
- Semantic search endpoints for job indexing, job search, and profile context retrieval.
- SQLAlchemy job model.
- SQLAlchemy application model linked one-to-one with jobs.
- SQLAlchemy profile model.
- SQLAlchemy generated asset model linked many-to-one with jobs.
- SQLAlchemy job embedding model linked one-to-one with jobs.
- Alembic migrations for the jobs, applications, profiles, generated assets, and job embeddings tables.
- Docker Compose PostgreSQL service.
- Swagger/OpenAPI availability tests.
- Job, application, profile, analysis, match scoring, CV suggestion, interview prep, LLM provider, generated asset, import, and semantic search endpoint tests.
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

## Manual Job Import

`POST /imports/jobs` accepts manually collected job payloads, normalizes the
incoming fields, skips duplicate jobs, and saves accepted records into the
existing `jobs` table. The app does not fetch jobs from public sources yet.
Future public-source imports should use allowed APIs or feeds only, without
scraping protected pages or automating login.

## Semantic Search

`POST /semantic-search/jobs/index` stores deterministic local vectors for the
current jobs. `POST /semantic-search/jobs/search` searches those indexed jobs,
and `POST /semantic-search/profile-context` retrieves the candidate profile
summary/projects that are most relevant to a selected job.

This is a tested foundation for later pgvector or Qdrant work. It does not call
an external embedding model yet.
