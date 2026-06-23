from datetime import datetime
from enum import Enum
from typing import Any, TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    Enum as SQLAlchemyEnum,
    ForeignKey,
    Integer,
    JSON,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.job import Job


class GeneratedAssetType(str, Enum):
    cv_suggestions = "cv_suggestions"
    cover_letter = "cover_letter"
    interview_prep = "interview_prep"


class GeneratedAsset(Base):
    __tablename__ = "generated_assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    asset_type: Mapped[GeneratedAssetType] = mapped_column(
        SQLAlchemyEnum(
            GeneratedAssetType,
            name="generated_asset_type",
            native_enum=False,
        ),
        nullable=False,
    )
    title: Mapped[str | None] = mapped_column(String(255))
    content: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    job: Mapped["Job"] = relationship(back_populates="generated_assets")
