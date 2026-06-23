from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.generated_asset import GeneratedAssetType


class GeneratedAssetBase(BaseModel):
    asset_type: GeneratedAssetType
    title: str | None = Field(default=None, max_length=255)
    content: dict[str, Any] = Field(..., min_length=1)


class GeneratedAssetCreate(GeneratedAssetBase):
    pass


class GeneratedAsset(GeneratedAssetBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int
    created_at: datetime
    updated_at: datetime
