from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.application import Application as ApplicationModel
from app.models.job import Job as JobModel
from app.schemas.application import Application, ApplicationCreate, ApplicationUpdate

router = APIRouter(prefix="/applications", tags=["applications"])


def _get_application_or_404(db: Session, application_id: int) -> ApplicationModel:
    application = db.get(ApplicationModel, application_id)
    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )
    return application


@router.post("", response_model=Application, status_code=status.HTTP_201_CREATED)
def create_application(
    application_create: ApplicationCreate,
    db: Session = Depends(get_db),
) -> ApplicationModel:
    job = db.get(JobModel, application_create.job_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    existing_application = db.scalar(
        select(ApplicationModel).where(
            ApplicationModel.job_id == application_create.job_id,
        ),
    )
    if existing_application is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Application already exists for this job",
        )

    application = ApplicationModel(**application_create.model_dump())
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


@router.get("", response_model=list[Application])
def list_applications(db: Session = Depends(get_db)) -> list[ApplicationModel]:
    return list(db.scalars(select(ApplicationModel).order_by(ApplicationModel.id)))


@router.get("/{application_id}", response_model=Application)
def get_application(
    application_id: int,
    db: Session = Depends(get_db),
) -> ApplicationModel:
    return _get_application_or_404(db, application_id)


@router.patch("/{application_id}", response_model=Application)
def update_application(
    application_id: int,
    application_update: ApplicationUpdate,
    db: Session = Depends(get_db),
) -> ApplicationModel:
    existing_application = _get_application_or_404(db, application_id)
    update_data = application_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(existing_application, field, value)

    db.commit()
    db.refresh(existing_application)
    return existing_application
