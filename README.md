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
- Stores generated outputs for later review.
- Imports manually collected jobs in bulk.
- Indexes jobs for local semantic-style search and retrieves relevant profile context.

## Current Status

Phase 13 is complete.

The app currently includes:

- A FastAPI backend.
- `GET /health`
- Database-backed job CRUD endpoints under `/jobs`
- Application tracking endpoints under `/applications`
- Profile management endpoints under `/profiles`
- Job description analysis endpoint under `/analysis/job`
- Match scoring endpoint under `/analysis/match`
- CV tailoring suggestion endpoint under `/analysis/cv-suggestions`
- Interview prep endpoint under `/analysis/interview-prep`
- Optional LLM provider interface with `none`, `fake`, and local `ollama` providers.
- Generated asset storage endpoints under `/jobs/{job_id}/generated-assets`
- Manual bulk job import endpoint under `/imports/jobs`
- Semantic search endpoints under `/semantic-search`
- Browser UI served by FastAPI at `/`
- Frontend assets served from `/static`
- SQLAlchemy ORM model for jobs.
- SQLAlchemy ORM model for applications with a one-to-one job relationship.
- SQLAlchemy ORM model for candidate profiles.
- SQLAlchemy ORM model for generated assets linked to jobs.
- SQLAlchemy ORM model for stored job embeddings.
- Alembic migrations for the `jobs`, `applications`, `profiles`, `generated_assets`, and `job_embeddings` tables.
- PostgreSQL configuration via `DATABASE_URL`.
- Docker Compose service for local PostgreSQL.
- Swagger/OpenAPI availability tests.
- Job, application, profile, analysis, match scoring, CV suggestion, interview prep, generated asset, import, semantic search, and frontend endpoint tests.
- A detailed build plan in [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md).

## Current Data Relationships

```text
profiles
|-- id
|-- target_roles
|-- skills
|-- experience_summary
`-- projects

jobs
|-- id
|-- title
|-- company
|-- description
|-- requirements
|-- seniority
`-- application 1:1
    |
    v
applications
|-- id
|-- job_id -> jobs.id
|-- status
|-- notes
|-- next_action
`-- deadline

jobs
`-- generated_assets 1:many
    |
    v
generated_assets
|-- id
|-- job_id -> jobs.id
|-- asset_type
|-- title
|-- content
|-- created_at
`-- updated_at

jobs
`-- job_embeddings 1:1
    |
    v
job_embeddings
|-- id
|-- job_id -> jobs.id
|-- content_hash
|-- embedding
|-- created_at
`-- updated_at
```

Match scoring does not create a database row yet. `POST /analysis/match` loads one
profile and one job, then calculates the match in the service layer:

```text
profiles.id  +  jobs.id
     |             |
     v             v
       /analysis/match
              |
              v
     score, strengths, gaps, recommendation
```

## Tech Stack

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- PostgreSQL
- pytest
- Rule-based NLP first, optional local LLM support through Ollama
- Optional deterministic fake LLM provider for tests and demos

## LLM and Ollama Setup

Phase 9 uses a provider pattern. The current LLM integration lives in
`app/services/llm_provider.py`, not in `app/cores/llama.py`.

```text
/analysis/cv-suggestions or /analysis/interview-prep
        |
        v
app/api/routes_analysis.py
        |
        v
rule-based CV or interview service
        |
        v
optional LLM provider
        |
        +-- LLM_PROVIDER=none   -> keep rule-based output
        +-- LLM_PROVIDER=fake   -> deterministic test/demo output
        `-- LLM_PROVIDER=ollama -> local Ollama text generation
```

The Ollama provider calls the local Ollama HTTP API at `/api/generate`. It is
used to improve CV suggestions and interview prep after the rule-based output
has already been built. If Ollama is unavailable, the app falls back to the
rule-based output.

`EMBEDDING_MODEL` is still reserved for future real embedding providers. Phase
12 currently uses a deterministic local embedding service in
`app/services/semantic_search.py` so the API can be tested without external AI
services, Qdrant, or a PostgreSQL extension.

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

Choose a database for local runtime.

Option A, PostgreSQL with Docker:

```powershell
docker compose up -d postgres
```

The default `DATABASE_URL` points to this local PostgreSQL service:

```text
postgresql+psycopg://careermatch:careermatch@localhost:5432/careermatch
```

Option B, SQLite for a quick local demo without PostgreSQL:

```powershell
$env:DATABASE_URL="sqlite:///./careermatch.db"
```

Use the SQLite command in the same PowerShell session where you run migrations
and start the API. If `DATABASE_URL` is not set, the app will try PostgreSQL.

Apply database migrations to the selected database:

```powershell
.\.venv\Scripts\alembic.exe upgrade head
```

Optional LLM provider setting:

```powershell
$env:LLM_PROVIDER="none"
```

Use `fake` only for deterministic local demos or tests. To use a free local
Ollama model, install Ollama, pull a text-generation model, then set:

```powershell
ollama pull llama3.2:3b
$env:LLM_PROVIDER="ollama"
$env:LLM_MODEL="llama3.2:3b"
$env:OLLAMA_BASE_URL="http://localhost:11434"
```

The app still works without an LLM API key. `EMBEDDING_MODEL` is also available
for later provider-backed vector search or RAG work, but the current CV and
interview endpoints use text generation through the LLM provider.

`POST /imports/jobs` imports manually collected job payloads, normalizes common
fields, skips duplicates, and saves accepted jobs into the existing `/jobs`
tracker. It does not fetch jobs from public sources yet.

Semantic search starts with `POST /semantic-search/jobs/index`, which stores
local job vectors in `job_embeddings`. After indexing, use
`POST /semantic-search/jobs/search` to find similar indexed jobs, or
`POST /semantic-search/profile-context` to retrieve the profile summary/projects
that best match a selected job.

Run tests:

```powershell
python -m pytest
```

Start the API:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Open:

```text
http://localhost:8000/
```

Health check:

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

If the browser shows a `500 Internal Server Error` for routes such as
`/applications`, check the database first. `GET /health` can pass even when the
database is unavailable because the health endpoint does not query tables.
Start PostgreSQL or set the SQLite `DATABASE_URL`, run Alembic migrations, then
restart the API.

## Safety Note

This project does not include mass auto-apply automation, LinkedIn scraping, Indeed scraping, login automation, CAPTCHA bypassing, or workflows that violate job board terms.

The user reviews all suggestions and submits applications manually.

## Project Docs

- [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md): detailed phase plan and future-session handoff.
- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md): short project overview.
