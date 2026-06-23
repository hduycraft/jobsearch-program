from pydantic import BaseModel, ConfigDict, Field

from app.schemas.job import Job


class ImportJobItem(BaseModel):
    title: str = Field(..., min_length=1)
    company: str = Field(..., min_length=1)
    location: str | None = None
    source_url: str | None = None
    description: str | None = None
    requirements: list[str] = Field(default_factory=list)
    seniority: str | None = None


class ManualJobImportRequest(BaseModel):
    source_name: str = Field(default="manual", min_length=1)
    jobs: list[ImportJobItem] = Field(..., min_length=1)


class SkippedImportJob(BaseModel):
    title: str
    company: str
    source_url: str | None = None
    reason: str


class ManualJobImportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    source_name: str
    imported_count: int
    skipped_count: int
    imported_jobs: list[Job]
    skipped_jobs: list[SkippedImportJob]
