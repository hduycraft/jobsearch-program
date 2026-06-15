from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class JobBase(BaseModel):
    title: str = Field(..., min_length=1)
    company: str = Field(..., min_length=1)
    location: str | None = None
    source: str | None = None
    source_url: str | None = None
    description: str | None = None
    requirements: list[str] = Field(default_factory=list)
    seniority: str | None = None


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    company: str | None = Field(default=None, min_length=1)
    location: str | None = None
    source: str | None = None
    source_url: str | None = None
    description: str | None = None
    requirements: list[str] | None = None
    seniority: str | None = None


class Job(JobBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date_found: datetime
    created_at: datetime
    updated_at: datetime
