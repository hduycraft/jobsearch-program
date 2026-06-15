from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProfileProject(BaseModel):
    name: str = Field(..., min_length=1)
    description: str | None = None
    skills: list[str] = Field(default_factory=list)
    url: str | None = None


class ProfileBase(BaseModel):
    target_roles: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    experience_summary: str | None = None
    projects: list[ProfileProject] = Field(default_factory=list)


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(BaseModel):
    target_roles: list[str] | None = None
    skills: list[str] | None = None
    experience_summary: str | None = None
    projects: list[ProfileProject] | None = None


class Profile(ProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
