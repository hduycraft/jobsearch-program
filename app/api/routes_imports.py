from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.imports import ManualJobImportRequest, ManualJobImportResponse
from app.services.job_importer import (
    build_manual_jobs_source,
    import_jobs,
)

router = APIRouter(prefix="/imports", tags=["imports"])


@router.post(
    "/jobs",
    response_model=ManualJobImportResponse,
    status_code=status.HTTP_201_CREATED,
)
def import_manual_jobs(
    import_request: ManualJobImportRequest,
    db: Session = Depends(get_db),
) -> ManualJobImportResponse:
    source = build_manual_jobs_source(import_request)
    result = import_jobs(db=db, source=source)

    return ManualJobImportResponse(
        source_name=result.source_name,
        imported_count=len(result.imported_jobs),
        skipped_count=len(result.skipped_jobs),
        imported_jobs=result.imported_jobs,
        skipped_jobs=result.skipped_jobs,
    )
