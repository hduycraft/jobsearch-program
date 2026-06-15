# CareerMatch Assistant

CareerMatch Assistant is a practical, resume-worthy, human-in-the-loop job-search and interview-preparation assistant.

The project is built in small working phases. Future sessions should read this roadmap first when continuing implementation, then inspect only the files needed for the current phase.

## Current Status

- Phase 3 is complete.
- The app has a minimal FastAPI backend and database-backed job tracker.
- `GET /health` returns `{"status": "ok"}`.
- Swagger UI and OpenAPI schema are covered by tests.
- Job CRUD endpoints are covered by tests.
- Job CRUD now uses SQLAlchemy persistence instead of in-memory storage.
- Application tracking endpoints are covered by tests.
- Application tracking uses a database-backed one-to-one relationship with jobs.
- Alembic is configured with an initial `jobs` table migration.
- Alembic includes an `applications` table migration.
- Docker Compose can start a local PostgreSQL database.
- Next phase: Phase 4, Profile Module.

## Ethical Scope

This project must stay human-in-the-loop.

Allowed:

- Paste or upload a CV/profile.
- Add job descriptions manually.
- Analyze profile/job match.
- Detect missing skills and knowledge gaps.
- Generate CV improvement suggestions.
- Generate interview prep questions and study topics.
- Track applications.
- Later, import jobs from safe public sources such as Greenhouse and Lever public APIs.

Not allowed:

- Mass auto-apply automation.
- LinkedIn scraping.
- Indeed scraping.
- Login automation.
- CAPTCHA bypassing.
- Any workflow that violates job board terms.

The user reviews all generated material and submits applications manually.

## Learning Goals

This project is designed to practice:

- Python backend development
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic migrations
- REST API design
- CV/job-description parsing
- Basic NLP and LLM workflows
- RAG/vector search later
- Clean project architecture
- Docker Compose
- Testing
- Writing a recruiter-friendly README

## Tech Stack

Backend:

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- PostgreSQL

AI/NLP:

- Start with rule-based keyword extraction and simple scoring.
- Later add an LLM provider interface.
- Optional providers later: OpenAI, Gemini, Ollama.
- Optional vector search later: Qdrant or pgvector.

Dev tools:

- Python virtual environment
- `requirements.txt`
- pytest
- Docker Compose later
- ruff or black optional

Frontend later:

- Next.js/React, or
- Streamlit if a faster demo UI is preferred.

## Current File Tree

```text
careermatch-assistant/
|-- app/
|   |-- __init__.py
|   |-- main.py
|   |-- api/
|   |   |-- __init__.py
|   |   |-- routes_applications.py
|   |   `-- routes_jobs.py
|   |-- core/
|   |   |-- __init__.py
|   |   |-- config.py
|   |   `-- database.py
|   |-- models/
|   |   |-- __init__.py
|   |   |-- application.py
|   |   `-- job.py
|   `-- schemas/
|       |-- __init__.py
|       |-- application.py
|       `-- job.py
|-- alembic/
|   |-- env.py
|   |-- script.py.mako
|   `-- versions/
|       |-- 0001_create_jobs_table.py
|       `-- 0002_create_applications_table.py
|-- tests/
|   |-- conftest.py
|   |-- test_applications.py
|   |-- test_jobs.py
|   `-- test_swagger.py
|-- .env.example
|-- alembic.ini
|-- docker-compose.yml
|-- PROJECT_ROADMAP.md
|-- README.md
`-- requirements.txt
```

## Target Backend Architecture

The project should grow toward this structure:

```text
careermatch-assistant/
|-- app/
|   |-- main.py
|   |-- core/
|   |   |-- config.py
|   |   `-- database.py
|   |-- models/
|   |   |-- job.py
|   |   |-- profile.py
|   |   |-- application.py
|   |   `-- generated_asset.py
|   |-- schemas/
|   |   |-- job.py
|   |   |-- profile.py
|   |   |-- application.py
|   |   `-- analysis.py
|   |-- services/
|   |   |-- cv_parser.py
|   |   |-- job_analyzer.py
|   |   |-- matcher.py
|   |   |-- interview_prep.py
|   |   `-- llm_provider.py
|   |-- api/
|   |   |-- routes_jobs.py
|   |   |-- routes_profiles.py
|   |   |-- routes_applications.py
|   |   `-- routes_analysis.py
|   `-- tests/
|-- alembic/
|-- .env.example
|-- requirements.txt
|-- PROJECT_ROADMAP.md
|-- README.md
`-- docker-compose.yml
```

If this is too much for a phase, simplify while keeping clear boundaries between routes, schemas, models, and services.

## Data Model Plan

Profile:

- `id`
- `name`
- `target_roles`
- `skills`
- `experience_summary`
- `projects`
- `created_at`
- `updated_at`

Job:

- `id`
- `title`
- `company`
- `location`
- `source`
- `source_url`
- `description`
- `requirements`
- `seniority`
- `date_found`
- `created_at`
- `updated_at`

JobMatch:

- `id`
- `job_id`
- `profile_id`
- `score`
- `strengths`
- `gaps`
- `recommendation`
- `created_at`

Application:

- `id`
- `job_id`
- `status`
- `notes`
- `next_action`
- `deadline`
- `applied_at`
- `created_at`
- `updated_at`

GeneratedAsset:

- `id`
- `job_id`
- `type`
- `content`
- `created_at`

Generated asset types:

- `cv_summary`
- `cv_bullets`
- `cover_letter`
- `interview_prep`
- `study_plan`

## Setup

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

Apply migrations:

```powershell
.\.venv\Scripts\alembic.exe upgrade head
```

Run tests:

```powershell
pytest
```

Run the API:

```powershell
uvicorn app.main:app --reload
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

Interactive API docs:

```text
http://localhost:8000/docs
```

## Phase Workflow

For each phase:

1. Start with a short plan before editing code.
2. Work on one phase only.
3. Keep the app runnable before moving on.
4. Explain the important concepts briefly.
5. Prefer small patches over full rewrites.
6. Add or update focused tests when behavior changes.
7. End with what changed, how to run/test, a commit message suggestion, and the next phase.

Each phase should include:

1. Goal
2. What I will learn
3. Files to create or edit
4. Implementation steps
5. Code changes
6. How to run/test
7. Common mistakes to watch for
8. Git commit message suggestion

## Phase Roadmap

### Phase 0: Project Setup - Complete

Goal: Create the basic FastAPI project and make sure the app runs.

Built:

- Python dependencies in `requirements.txt`
- FastAPI app in `app/main.py`
- Health check endpoint
- Basic Swagger/OpenAPI tests
- Setup instructions in README and roadmap

Endpoint:

- `GET /health`

Expected result:

```json
{
  "status": "ok"
}
```

Learning focus:

- FastAPI app structure
- Virtual environments
- Dependency installation
- Running a local API server
- Health check endpoints
- Swagger/OpenAPI basics

Common mistakes:

- Forgetting to activate the virtual environment.
- Running `uvicorn main:app --reload` instead of `uvicorn app.main:app --reload`.
- Opening `/health` before the server has finished starting.

Commit message suggestion:

```text
Initialize FastAPI project with health check
```

### Phase 1: Basic Job Tracker Without Database - Complete

Goal: Create an in-memory job tracker before adding database complexity.

Built:

- Pydantic job schemas
- Jobs API router
- In-memory dictionary/list storage
- CRUD endpoints

Endpoints:

- `POST /jobs`
- `GET /jobs`
- `GET /jobs/{job_id}`
- `PATCH /jobs/{job_id}`
- `DELETE /jobs/{job_id}`

Learning focus:

- REST API design
- Pydantic request/response models
- CRUD basics
- FastAPI routers

Expected result:

- A job can be added manually and retrieved from the API.

Suggested files:

- `app/schemas/job.py`
- `app/api/routes_jobs.py`
- `app/main.py`
- `tests/test_jobs.py`

Commit message suggestion:

```text
Add in-memory job tracker endpoints
```

### Phase 2: Add PostgreSQL and SQLAlchemy - Complete

Goal: Replace in-memory storage with a real database.

Built:

- Database connection
- SQLAlchemy models
- Alembic migrations
- Job table
- Database-backed job CRUD
- PostgreSQL Docker Compose service
- Test database override using SQLite for fast isolated tests

Learning focus:

- Relational database basics
- SQLAlchemy ORM
- Alembic migrations
- Environment variables
- Database sessions

Expected result:

- Jobs persist after restarting the server.

Suggested files:

- `app/core/config.py`
- `app/core/database.py`
- `app/models/job.py`
- `alembic/`
- `.env.example`
- `docker-compose.yml` if PostgreSQL is added here

Commit message suggestion:

```text
Persist jobs with PostgreSQL and SQLAlchemy
```

### Phase 3: Application Tracker - Complete

Goal: Track job application progress.

Built:

- Application model
- Application schemas
- Application routes
- Status enum
- Relationship from job to application

Statuses:

- `saved`
- `interested`
- `cv_tailored`
- `applied`
- `interview`
- `rejected`
- `offer`
- `archived`

Endpoints:

- `POST /applications`
- `GET /applications`
- `GET /applications/{application_id}`
- `PATCH /applications/{application_id}`

Learning focus:

- Relationships between tables
- Job-to-application relationship
- Status tracking

Expected result:

- Each job can have application tracking information.

Implemented behavior:

- One application tracking record can be created for each job.
- Creating an application for a missing job returns `404`.
- Creating a second application for the same job returns `409`.
- Application status, notes, next action, deadline, and applied timestamp can be updated.

Commit message suggestion:

```text
Add application tracking
```

### Phase 4: Profile Module

Goal: Store a career profile for matching.

Build:

- Profile model
- Profile schemas
- Profile routes

Profile should include:

- Target roles
- Skills
- Experience summary
- Projects

Endpoints:

- `POST /profiles`
- `GET /profiles`
- `GET /profiles/{profile_id}`
- `PATCH /profiles/{profile_id}`

Learning focus:

- Modeling profile data
- Storing structured skills and projects
- Preparing data for matching

Expected result:

- A career profile can be stored and used later for matching.

Commit message suggestion:

```text
Add profile management endpoints
```

### Phase 5: Job Description Analyzer

Goal: Analyze a job description using simple rule-based NLP.

Build:

- `job_analyzer.py`
- Skill extraction
- Seniority detection
- Common requirement detection

Initial skill list:

- Python
- FastAPI
- SQL
- PostgreSQL
- Docker
- Azure
- Azure DevOps
- Git
- REST API
- Machine Learning
- NLP
- RAG
- LLM
- React
- Next.js

Endpoint:

- `POST /analysis/job`

Input:

- Job description text

Output:

- Extracted skills
- Seniority estimate
- Summary of requirements

Learning focus:

- Simple NLP
- Text normalization
- Keyword extraction
- API service layer

Expected result:

- Given a job description, the system extracts useful skills and requirements.

Commit message suggestion:

```text
Add rule-based job description analyzer
```

### Phase 6: Match Scoring

Goal: Compare a profile against a job description and return a match score.

Build:

- `matcher.py`
- Compare profile skills with extracted job skills
- Calculate score
- Return strengths and gaps

Simple scoring:

- Skill match: 60%
- Target role/seniority match: 20%
- Project relevance: 20%

Endpoint:

- `POST /analysis/match`

Input:

- `profile_id`
- `job_id`

Output:

- Score
- Matched skills
- Missing skills
- Strengths
- Gaps
- Recommendation

Learning focus:

- Business logic design
- Scoring algorithms
- Explainable recommendations

Expected result:

- The app can say whether a job is suitable and why.

Commit message suggestion:

```text
Add explainable profile job match scoring
```

### Phase 7: CV Tailoring Suggestions

Goal: Generate suggestions for improving a CV for a specific job without using an LLM first.

Build:

- Compare missing job skills with profile data
- Suggest projects or experience to highlight
- Generate template-based CV bullet suggestions
- Warn the user not to fake experience

Endpoint:

- `POST /analysis/cv-suggestions`

Output:

- Tailored summary suggestion
- Bullet point suggestions
- Missing keyword warnings
- Ethical warning not to invent experience

Learning focus:

- Template generation
- Practical CV tailoring logic
- Ethical AI/application behavior

Expected result:

- The app gives useful CV improvement suggestions based on real profile data.

Commit message suggestion:

```text
Add rule-based CV tailoring suggestions
```

### Phase 8: Interview Prep Generator

Goal: Generate interview preparation materials for a selected job.

Build:

- `interview_prep.py`
- Likely technical questions by required skill
- HR questions
- Study checklist
- 3-day preparation plan

Endpoint:

- `POST /analysis/interview-prep`

Output:

- Likely technical questions
- Likely HR questions
- Study topics
- Weak areas
- 3-day preparation plan

Learning focus:

- Mapping job requirements to study plans
- Interview preparation logic
- Reusable service design

Expected result:

- The app helps identify what to study before an interview.

Commit message suggestion:

```text
Add interview preparation generator
```

### Phase 9: Add LLM Provider Interface

Goal: Add optional LLM support without making the app dependent on one provider.

Build:

- `llm_provider.py`
- Base provider interface
- Fake/mock provider for tests
- Optional provider selection from environment variables
- Graceful rule-based fallback

Important:

- The app must still work without an LLM API key.

Use LLM support for:

- Better CV suggestions
- Better interview questions
- Cover letter drafts
- Job summaries

Learning focus:

- Abstraction
- Provider pattern
- Environment configuration
- Graceful fallback

Expected result:

- The system can use AI generation if configured, but still works with rule-based logic.

Commit message suggestion:

```text
Add optional LLM provider interface
```

### Phase 10: Generated Asset Storage

Goal: Store generated outputs.

Build:

- GeneratedAsset model
- Routes to list generated outputs per job
- Save CV suggestions, cover letters, and interview prep

Endpoints:

- `GET /jobs/{job_id}/generated-assets`
- `POST /jobs/{job_id}/generated-assets`

Learning focus:

- Saving AI outputs
- Linking generated content to jobs
- Auditability

Expected result:

- Previously generated interview prep or CV suggestions can be viewed for a job.

Commit message suggestion:

```text
Add generated asset storage
```

### Phase 11: Safe Job Import From Public APIs

Goal: Import jobs from safe public job board APIs.

Start with:

- Greenhouse public job board API
- Lever postings API

Build:

- `job_importer.py`
- Import jobs from configured company boards
- Deduplicate by URL/title/company
- Save imported jobs

Endpoints:

- `POST /imports/greenhouse`
- `POST /imports/lever`

Important:

- Do not scrape LinkedIn or Indeed.
- Do not automate login.
- Do not auto-apply.

Learning focus:

- External API integration
- Data cleaning
- Deduplication
- Background ingestion design

Expected result:

- Jobs can be imported from selected companies into the tracker.

Commit message suggestion:

```text
Add safe public ATS job imports
```

### Phase 12: Optional Vector Search / RAG

Goal: Add semantic search over jobs, CV, and project data.

Choose one:

- Qdrant
- pgvector

Build:

- Embedding service
- Store job description embeddings
- Search similar jobs
- Retrieve relevant profile/project context for a selected job

Use cases:

- Find jobs similar to one the user liked
- Retrieve the most relevant project for a job
- Generate grounded application suggestions

Learning focus:

- Embeddings
- Vector search
- RAG architecture
- Semantic matching

Expected result:

- The app can retrieve relevant experience and jobs semantically, not only by keywords.

Commit message suggestion:

```text
Add semantic job search foundation
```

### Phase 13: Frontend

Goal: Build a simple demo-friendly user interface.

Preferred:

- Next.js
- Tailwind CSS
- shadcn/ui

Pages:

- Dashboard
- Jobs
- Job detail
- Profile
- Match analysis
- Interview prep
- Application tracker

Learning focus:

- Frontend/backend integration
- API clients
- UI state
- Practical product design

Expected result:

- The project becomes demo-friendly for recruiters.

Commit message suggestion:

```text
Add initial frontend interface
```

### Phase 14: Docker and Deployment

Goal: Make the project easy to run and show.

Build:

- Dockerfile
- `docker-compose.yml`
- PostgreSQL container
- Optional Redis container
- README deployment instructions

Optional:

- Azure App Service
- Azure DevOps pipeline
- GitHub Actions

Learning focus:

- Deployment basics
- Environment configuration
- CI/CD
- Containerization

Expected result:

- Someone can clone and run the project easily.

Commit message suggestion:

```text
Add Docker setup and deployment notes
```

## README Improvement Checklist

As the MVP grows, keep adding:

- Project overview
- Problem statement
- Features
- Architecture diagram
- Tech stack
- Setup instructions
- API examples
- Screenshots or demo GIF
- What I learned
- Future improvements
- Ethical note
- Resume positioning

## Resume Positioning Draft

When the MVP is done, adapt bullets like:

- Built an AI-powered job-search assistant using FastAPI, PostgreSQL, and LLM-based analysis to match job descriptions against a candidate profile.
- Implemented job tracking, skill-gap detection, CV tailoring suggestions, and interview preparation generation.
- Designed a human-in-the-loop workflow for reviewing application materials before submission.
- Added structured job import from public ATS APIs and explainable match scoring.

## Notes for Future Codex Sessions

- Read this roadmap first when continuing implementation.
- For a short public-facing explanation, read `README.md`.
- For a short project overview, read `PROJECT_OVERVIEW.md`.
- Confirm the current phase before editing.
- Do not scan the whole project unless the README and target files are insufficient.
- Keep work phase-based and runnable.
- Use concise explanations before coding.
- Never add unsafe scraping, login automation, or auto-apply behavior.
- At the end of each phase, summarize completed work, test command, commit message, and next phase.
