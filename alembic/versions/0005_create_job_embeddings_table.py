"""create job embeddings table

Revision ID: 0005_create_job_embeddings_table
Revises: 0004_create_generated_assets_table
Create Date: 2026-06-23

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0005_create_job_embeddings_table"
down_revision: str | None = "0004_create_generated_assets_table"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "job_embeddings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("embedding", sa.JSON(), nullable=False),
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
        sa.UniqueConstraint("job_id"),
    )
    op.create_index(
        op.f("ix_job_embeddings_id"),
        "job_embeddings",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_job_embeddings_job_id"),
        "job_embeddings",
        ["job_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_job_embeddings_job_id"), table_name="job_embeddings")
    op.drop_index(op.f("ix_job_embeddings_id"), table_name="job_embeddings")
    op.drop_table("job_embeddings")
