from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.job import Job as JobModel
from app.models.profile import Profile as ProfileModel
from app.schemas.semantic_search import (
    JobEmbeddingIndexResponse,
    ProfileContextRequest,
    ProfileContextResponse,
    SemanticJobSearchRequest,
    SemanticJobSearchResponse,
)
from app.services.semantic_search import (
    index_job_embeddings,
    retrieve_profile_context,
    search_indexed_jobs,
)

router = APIRouter(prefix="/semantic-search", tags=["semantic-search"])


@router.post("/jobs/index", response_model=JobEmbeddingIndexResponse)
def index_jobs_for_semantic_search(
    db: Session = Depends(get_db),
) -> dict[str, object]:
    indexed_embeddings = index_job_embeddings(db)
    return {
        "indexed_count": len(indexed_embeddings),
        "embeddings": indexed_embeddings,
    }


@router.post("/jobs/search", response_model=SemanticJobSearchResponse)
def search_jobs(
    request: SemanticJobSearchRequest,
    db: Session = Depends(get_db),
) -> dict[str, object]:
    return {
        "query": request.query,
        "results": search_indexed_jobs(
            db=db,
            query=request.query,
            limit=request.limit,
        ),
    }


@router.post("/profile-context", response_model=ProfileContextResponse)
def get_profile_context(
    request: ProfileContextRequest,
    db: Session = Depends(get_db),
) -> dict[str, object]:
    profile = db.get(ProfileModel, request.profile_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    job = db.get(JobModel, request.job_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    return {
        "profile_id": request.profile_id,
        "job_id": request.job_id,
        "context_items": retrieve_profile_context(
            profile=profile,
            job=job,
            limit=request.limit,
        ),
    }
