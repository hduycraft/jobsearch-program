from fastapi import FastAPI

from app.api.routes_analysis import router as analysis_router
from app.api.routes_applications import router as applications_router
from app.api.routes_generated_assets import router as generated_assets_router
from app.api.routes_imports import router as imports_router
from app.api.routes_jobs import router as jobs_router
from app.api.routes_profiles import router as profiles_router

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


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
