# CareerMatch Assistant

CareerMatch Assistant is a practical, resume-worthy, human-in-the-loop job-search and interview-preparation assistant.

The project is built in small working phases. Future sessions should read this roadmap first when continuing implementation, then inspect only the files needed for the current phase.

## Current Status

- Phase 12 is complete.
- The app has a minimal FastAPI backend and database-backed job tracker.
- `GET /health` returns `{"status": "ok"}`.
- Swagger UI and OpenAPI schema are covered by tests.
- Job CRUD endpoints are covered by tests.
- Job CRUD now uses SQLAlchemy persistence instead of in-memory storage.
- Application tracking endpoints are covered by tests.
- Application tracking uses a database-backed one-to-one relationship with jobs.
- Profile management endpoints are covered by tests.
- Profiles store target roles, skills, experience summaries, and structured projects.
- Job description analysis endpoint is covered by tests.
- Job descriptions can be analyzed for known skills, seniority, and requirement summaries.
- Match scoring endpoint is covered by tests.
- Profiles can be compared against jobs with explainable strengths, gaps, and recommendations.
- CV tailoring suggestion endpoint is covered by tests.
- CV suggestions produce grounded summaries, project highlights, bullet ideas, missing keyword warnings, and an ethical warning.
- Interview prep endpoint is covered by tests.
- Interview prep generates technical questions, HR questions, study topics, weak areas, and a 3-day preparation plan.
- Optional LLM provider interface is covered by tests.
- LLM provider selection supports `none`, deterministic `fake`, and local `ollama` providers.
- Ollama support lives in `app/services/llm_provider.py`; no separate `app/cores/llama.py` file is required.
- CV suggestions and interview prep can use an optional LLM provider while falling back to rule-based output.
- Generated asset storage endpoints are covered by tests.
- Generated assets store CV suggestions, cover letters, and interview prep JSON output per job.
- Manual bulk job import endpoint is covered by tests.
- Job imports normalize manually collected job payloads, save accepted jobs, and skip duplicates.
- Semantic search endpoints are covered by tests.
- Job embeddings are stored in the database as deterministic local vectors.
- Similar indexed jobs can be searched through `/semantic-search/jobs/search`.
- Relevant profile summary/project context can be retrieved for a selected job.
- Alembic is configured with an initial `jobs` table migration.
- Alembic includes an `applications` table migration.
- Alembic includes a `profiles` table migration.
- Alembic includes a `generated_assets` table migration.
- Alembic includes a `job_embeddings` table migration.
- Docker Compose can start a local PostgreSQL database.
- Next phase: Phase 13, Frontend.

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
- Import manually collected jobs in bulk.

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
- LLM provider interface supports `none`, `fake`, and local `ollama`.
- Ollama uses the local HTTP API through `app/services/llm_provider.py`.
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
|   |   |-- routes_analysis.py
|   |   |-- routes_applications.py
|   |   |-- routes_generated_assets.py
|   |   |-- routes_imports.py
|   |   |-- routes_jobs.py
|   |   |-- routes_profiles.py
|   |   `-- routes_semantic_search.py
|   |-- core/
|   |   |-- __init__.py
|   |   |-- config.py
|   |   `-- database.py
|   |-- models/
|   |   |-- __init__.py
|   |   |-- application.py
|   |   |-- generated_asset.py
|   |   |-- job.py
|   |   |-- job_embedding.py
|   |   `-- profile.py
|   |-- schemas/
|       |-- __init__.py
|       |-- analysis.py
|       |-- application.py
|       |-- generated_asset.py
|       |-- imports.py
|       |-- job.py
|       |-- profile.py
|       `-- semantic_search.py
|   `-- services/
|       |-- __init__.py
|       |-- cv_tailor.py
|       |-- interview_prep.py
|       |-- job_analyzer.py
|       |-- job_importer.py
|       |-- llm_provider.py
|       |-- matcher.py
|       `-- semantic_search.py
|-- alembic/
|   |-- env.py
|   |-- script.py.mako
|   `-- versions/
|       |-- 0001_create_jobs_table.py
|       |-- 0002_create_applications_table.py
|       |-- 0003_create_profiles_table.py
|       |-- 0004_create_generated_assets_table.py
|       `-- 0005_create_job_embeddings_table.py
|-- tests/
|   |-- conftest.py
|   |-- test_analysis.py
|   |-- test_applications.py
|   |-- test_generated_assets.py
|   |-- test_imports.py
|   |-- test_jobs.py
|   |-- test_llm_provider.py
|   |-- test_profiles.py
|   |-- test_semantic_search.py
|   `-- test_swagger.py
|-- .env.example
|-- alembic.ini
|-- docker-compose.yml
|-- PROJECT_ROADMAP.md
|-- PROJECT_OVERVIEW.md
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
|   |   |-- generated_asset.py
|   |   |-- imports.py
|   |   `-- analysis.py
|   |-- services/
|   |   |-- cv_parser.py
|   |   |-- job_analyzer.py
|   |   |-- matcher.py
|   |   |-- interview_prep.py
|   |   |-- job_importer.py
|   |   `-- llm_provider.py
|   |-- api/
|   |   |-- routes_jobs.py
|   |   |-- routes_profiles.py
|   |   |-- routes_applications.py
|   |   |-- routes_generated_assets.py
|   |   |-- routes_imports.py
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
- `asset_type`
- `title`
- `content`
- `created_at`
- `updated_at`

Generated asset types:

- `cv_suggestions`
- `cover_letter`
- `interview_prep`

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

### Phase 4: Profile Module - Complete

Goal: Store a career profile for matching.

Built:

- Profile model
- Profile schemas
- Profile routes
- Alembic migration for the `profiles` table
- Profile endpoint tests

Profile includes:

- Target roles
- Skills
- Experience summary
- Structured projects with name, description, skills, and URL

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

Implemented behavior:

- Profiles can be created with target roles, skills, experience summary, and projects.
- Profile list and detail endpoints return stored profiles.
- Profile patch updates only the fields sent in the request.
- Missing profile IDs return `404`.
- Empty profile creation defaults list fields to empty lists.

Commit message suggestion:

```text
Add profile management endpoints
```

### Phase 5: Job Description Analyzer - Complete

Goal: Analyze a job description using simple rule-based NLP.

Built:

- `job_analyzer.py`
- Skill extraction
- Seniority detection
- Common requirement detection
- Analysis schemas
- Analysis API router
- Endpoint tests

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

Implemented behavior:

- `POST /analysis/job` accepts raw job description text.
- The analyzer extracts known skills from the initial roadmap skill list.
- The analyzer estimates seniority from explicit seniority words or years of experience.
- The analyzer returns a short list of requirement-like sentences or bullet lines.
- The endpoint is included in the OpenAPI schema.

Commit message suggestion:

```text
Add rule-based job description analyzer
```

### Phase 6: Match Scoring - Complete

Goal: Compare a profile against a job description and return a match score.

Built:

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

Implemented behavior:

- `POST /analysis/match` accepts a `profile_id` and `job_id`.
- The matcher loads the stored profile and job from the database.
- Job skills are extracted with the existing rule-based job analyzer.
- Scoring uses the Phase 6 weighting: skill match 60%, target role match 20%, and project relevance 20%.
- The response includes score breakdown, matched skills, missing skills, strengths, gaps, and a recommendation.
- Missing profile IDs return `404`.
- Missing job IDs return `404`.

Commit message suggestion:

```text
Add explainable profile job match scoring
```

### Phase 7: CV Tailoring Suggestions - Complete

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

Implemented behavior:

- `POST /analysis/cv-suggestions` accepts a `profile_id` and `job_id`.
- The endpoint loads the stored profile and job from the database.
- The CV tailoring service reuses rule-based job analysis and match scoring outputs.
- The response includes a tailored summary suggestion, projects to highlight, CV bullet suggestions, missing keyword warnings, and an ethical warning.
- Missing profile IDs return `404`.
- Missing job IDs return `404`.

Commit message suggestion:

```text
Add rule-based CV tailoring suggestions
```

### Phase 8: Interview Prep Generator - Complete

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

Implemented behavior:

- `POST /analysis/interview-prep` accepts a `profile_id` and `job_id`.
- The endpoint loads the stored profile and job from the database.
- The interview prep service reuses rule-based job analysis and match scoring outputs.
- The response includes likely technical questions by required skill, HR questions, study topics, weak areas, and a 3-day preparation plan.
- Missing profile IDs return `404`.
- Missing job IDs return `404`.

Commit message suggestion:

```text
Add interview preparation generator
```

### Phase 9: Add LLM Provider Interface - Complete

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

Implemented behavior:

- `LLM_PROVIDER=none` keeps the app fully rule-based.
- `LLM_PROVIDER=fake` selects a deterministic fake provider for tests and demos.
- `LLM_PROVIDER=ollama` uses a free local Ollama text-generation model through the local Ollama HTTP API.
- `LLM_MODEL`, `OLLAMA_BASE_URL`, and `LLM_TIMEOUT_SECONDS` configure the local Ollama provider.
- `EMBEDDING_MODEL` is available for later vector search or RAG work.
- The current setup does not use `app/cores/llama.py` or LlamaIndex; those would only be needed later for dedicated embedding/RAG setup.
- CV suggestions and interview prep receive an optional provider through FastAPI dependency injection.
- Provider failures, missing provider output, or unknown provider names fall back to rule-based output.
- The provider interface includes future hooks for CV suggestions, interview prep, cover letter drafts, and job summaries.

Commit message suggestion:

```text
Add optional LLM provider interface
```

### Phase 10: Generated Asset Storage - Complete

Goal: Store generated outputs.

Built:

- GeneratedAsset model
- Routes to list generated outputs per job
- Save CV suggestions, cover letters, and interview prep
- Alembic migration for `generated_assets`
- Endpoint tests for creating, listing, missing jobs, invalid asset types, and job delete cleanup

Endpoints:

- `GET /jobs/{job_id}/generated-assets`
- `POST /jobs/{job_id}/generated-assets`

Learning focus:

- Saving AI outputs
- Linking generated content to jobs
- Auditability

Expected result:

- Previously generated interview prep or CV suggestions can be viewed for a job.
- Generated assets are stored as JSON content linked to `jobs.id`.

Commit message suggestion:

```text
Add generated asset storage
```

### Phase 11: Manual Job Import - Complete

Goal: Import manually collected jobs in bulk without splitting by region.

Start with:

- Jobs the user has already collected manually
- A simple source label such as `manual`, `spreadsheet`, or `manual-bulk-import`
- No external fetching

Future sources to evaluate later:

- Official public APIs or feeds, if their terms allow automated fetching
- Greenhouse or Lever public job board APIs, only where automated API access is allowed
- Company ATS APIs or feeds that explicitly permit this use

Build:

- `job_importer.py`
- Source adapter interface for manually provided jobs
- Import jobs from request payloads
- Normalize title, company, location, source, source URL, description, and requirements
- Deduplicate by URL/title/company
- Save imported jobs
- Endpoint tests for successful imports, default source labels, duplicate skipping, and validation

Endpoints:

- `POST /imports/jobs`
- Later source-specific endpoints only if needed, such as `POST /imports/greenhouse` or `POST /imports/lever`

Implemented behavior:

- `POST /imports/jobs` accepts manually collected job payloads and saves accepted jobs into the existing `jobs` table.
- The endpoint does not fetch jobs from public sources.
- The endpoint does not split imports by region.
- Incoming title, company, location, description, requirements, and seniority values are normalized before save.
- Requirements are cleaned and deduplicated while preserving the original order.
- Existing jobs are deduplicated by source URL when present, and by title/company.
- Duplicate jobs are reported in `skipped_jobs` instead of being saved.
- No scraping, login automation, protected page fetching, LinkedIn scraping, or Indeed scraping was added.

Important:

- This phase is manual import only.
- Future automated imports should use only public APIs, public feeds, or sources whose terms allow automated fetching.
- Do not scrape protected pages or bypass anti-bot controls.
- Do not scrape LinkedIn or Indeed.
- Do not automate login.
- Do not auto-apply.

Learning focus:

- Data cleaning
- Deduplication
- Bulk import API design
- Keeping import logic separate from route logic

Expected result:

- Manually collected jobs can be imported into the tracker in bulk.
- Live external APIs can be added later behind the same service boundary if the source allows automated fetching.

Commit message suggestion:

```text
Add manual job imports
```

### Phase 12: Optional Vector Search / RAG - Complete

Goal: Add semantic search over jobs, CV, and project data.

Chosen foundation:

- Database-backed local vector storage in `job_embeddings`.
- Vectors are stored as JSON for SQLite test compatibility and to keep this phase runnable without PostgreSQL extensions.
- The service boundary can be replaced later with pgvector or Qdrant.

Built:

- `app/services/semantic_search.py`
- Deterministic local embedding service
- `JobEmbedding` model
- Alembic migration for the `job_embeddings` table
- Semantic search schemas
- Semantic search API router
- Endpoint tests

Use cases:

- Find jobs similar to one the user liked
- Retrieve the most relevant project for a job
- Generate grounded application suggestions

Endpoints:

- `POST /semantic-search/jobs/index`
- `POST /semantic-search/jobs/search`
- `POST /semantic-search/profile-context`

Implemented behavior:

- `POST /semantic-search/jobs/index` creates or refreshes stored vectors for all current jobs.
- Job embedding rows are deduplicated by `job_id` and refreshed when job text changes.
- `POST /semantic-search/jobs/search` compares a query vector against stored job vectors and returns the closest indexed jobs.
- `POST /semantic-search/profile-context` compares a selected job against the profile experience summary and projects, then returns the most relevant context items.
- Missing profile IDs return `404`.
- Missing job IDs return `404`.
- The first implementation is deterministic and local. It is a foundation for later real embeddings through pgvector or Qdrant, not a full external RAG stack yet.

Learning focus:

- Embeddings
- Vector search
- RAG architecture
- Semantic matching

Expected result:

- The app can retrieve relevant experience and indexed jobs through vector similarity without requiring external services.

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
