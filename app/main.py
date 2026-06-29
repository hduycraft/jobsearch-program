from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes_analysis import router as analysis_router
from app.api.routes_applications import router as applications_router
from app.api.routes_generated_assets import router as generated_assets_router
from app.api.routes_imports import router as imports_router
from app.api.routes_jobs import router as jobs_router
from app.api.routes_profiles import router as profiles_router
from app.api.routes_semantic_search import router as semantic_search_router

app = FastAPI(
    title="CareerMatch Assistant",
    description="Human-in-the-loop job-search and interview-preparation assistant.",
    version="0.1.0",
)

app.include_router(analysis_router)
app.include_router(applications_router)
app.include_router(generated_assets_router)
app.include_router(imports_router)
app.include_router(jobs_router)
app.include_router(profiles_router)
app.include_router(semantic_search_router)

FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def frontend() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")
