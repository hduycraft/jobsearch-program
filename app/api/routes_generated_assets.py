from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.generated_asset import GeneratedAsset as GeneratedAssetModel
from app.models.job import Job as JobModel
from app.schemas.generated_asset import GeneratedAsset, GeneratedAssetCreate

router = APIRouter(
    prefix="/jobs/{job_id}/generated-assets",
    tags=["generated-assets"],
)


def _get_job_or_404(db: Session, job_id: int) -> JobModel:
    job = db.get(JobModel, job_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    return job


@router.post("", response_model=GeneratedAsset, status_code=status.HTTP_201_CREATED)
def create_generated_asset(
    job_id: int,
    generated_asset_create: GeneratedAssetCreate,
    db: Session = Depends(get_db),
) -> GeneratedAssetModel:
    _get_job_or_404(db, job_id)

    generated_asset = GeneratedAssetModel(
        job_id=job_id,
        **generated_asset_create.model_dump(),
    )
    db.add(generated_asset)
    db.commit()
    db.refresh(generated_asset)
    return generated_asset


@router.get("", response_model=list[GeneratedAsset])
def list_generated_assets(
    job_id: int,
    db: Session = Depends(get_db),
) -> list[GeneratedAssetModel]:
    _get_job_or_404(db, job_id)

    return list(
        db.scalars(
            select(GeneratedAssetModel)
            .where(GeneratedAssetModel.job_id == job_id)
            .order_by(GeneratedAssetModel.id),
        ),
    )
