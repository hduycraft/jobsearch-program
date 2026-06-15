from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.job import Job as JobModel
from app.schemas.job import Job, JobCreate, JobUpdate

router = APIRouter(prefix="/jobs", tags=["jobs"])


def _get_job_or_404(db: Session, job_id: int) -> JobModel:
    job = db.get(JobModel, job_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    return job


@router.post("", response_model=Job, status_code=status.HTTP_201_CREATED)
def create_job(job_create: JobCreate, db: Session = Depends(get_db)) -> JobModel:
    job = JobModel(**job_create.model_dump())
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.get("", response_model=list[Job])
def list_jobs(db: Session = Depends(get_db)) -> list[JobModel]:
    return list(db.scalars(select(JobModel).order_by(JobModel.id)))


@router.get("/{job_id}", response_model=Job)
def get_job(job_id: int, db: Session = Depends(get_db)) -> JobModel:
    return _get_job_or_404(db, job_id)


@router.patch("/{job_id}", response_model=Job)
def update_job(
    job_id: int,
    job_update: JobUpdate,
    db: Session = Depends(get_db),
) -> JobModel:
    existing_job = _get_job_or_404(db, job_id)
    update_data = job_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(existing_job, field, value)

    db.commit()
    db.refresh(existing_job)
    return existing_job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(job_id: int, db: Session = Depends(get_db)) -> Response:
    job = _get_job_or_404(db, job_id)
    db.delete(job)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
