from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.job import Job as JobModel
from app.models.profile import Profile as ProfileModel
from app.schemas.analysis import (
    CvSuggestionsRequest,
    CvSuggestionsResponse,
    InterviewPrepRequest,
    InterviewPrepResponse,
    JobAnalysisRequest,
    JobAnalysisResponse,
    MatchRequest,
    MatchResponse,
)
from app.services.cv_tailor import build_cv_suggestions
from app.services.interview_prep import build_interview_prep
from app.services.job_analyzer import analyze_job_description
from app.services.llm_provider import LLMProvider, get_llm_provider
from app.services.matcher import match_profile_to_job

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/job", response_model=JobAnalysisResponse)
def analyze_job(request: JobAnalysisRequest) -> dict[str, object]:
    return analyze_job_description(request.description)


@router.post("/match", response_model=MatchResponse)
def match_job(request: MatchRequest, db: Session = Depends(get_db)) -> dict[str, object]:
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

    return match_profile_to_job(profile, job)


@router.post("/cv-suggestions", response_model=CvSuggestionsResponse)
def suggest_cv_updates(
    request: CvSuggestionsRequest,
    db: Session = Depends(get_db),
    llm_provider: LLMProvider = Depends(get_llm_provider),
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

    return build_cv_suggestions(profile, job, llm_provider=llm_provider)


@router.post("/interview-prep", response_model=InterviewPrepResponse)
def prepare_for_interview(
    request: InterviewPrepRequest,
    db: Session = Depends(get_db),
    llm_provider: LLMProvider = Depends(get_llm_provider),
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

    return build_interview_prep(profile, job, llm_provider=llm_provider)
