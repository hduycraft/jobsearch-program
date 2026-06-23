"""create generated assets table

Revision ID: 0004_create_generated_assets_table
Revises: 0003_create_profiles_table
Create Date: 2026-06-23

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0004_create_generated_assets_table"
down_revision: str | None = "0003_create_profiles_table"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "generated_assets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column(
            "asset_type",
            sa.Enum(
                "cv_suggestions",
                "cover_letter",
                "interview_prep",
                name="generated_asset_type",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("content", sa.JSON(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_generated_assets_id"),
        "generated_assets",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_generated_assets_job_id"),
        "generated_assets",
        ["job_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_generated_assets_job_id"), table_name="generated_assets")
    op.drop_index(op.f("ix_generated_assets_id"), table_name="generated_assets")
    op.drop_table("generated_assets")
