from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.application import ApplicationStatus


class ApplicationBase(BaseModel):
    status: ApplicationStatus = ApplicationStatus.saved
    notes: str | None = None
    next_action: str | None = None
    deadline: datetime | None = None
    applied_at: datetime | None = None


class ApplicationCreate(ApplicationBase):
    job_id: int


class ApplicationUpdate(BaseModel):
    status: ApplicationStatus | None = None
    notes: str | None = None
    next_action: str | None = None
    deadline: datetime | None = None
    applied_at: datetime | None = None


class Application(ApplicationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int
    created_at: datetime
    updated_at: datetime
