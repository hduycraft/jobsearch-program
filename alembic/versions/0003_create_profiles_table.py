"""create profiles table

Revision ID: 0003_create_profiles_table
Revises: 0002_create_applications_table
Create Date: 2026-06-15

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0003_create_profiles_table"
down_revision: str | None = "0002_create_applications_table"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("target_roles", sa.JSON(), nullable=False),
        sa.Column("skills", sa.JSON(), nullable=False),
        sa.Column("experience_summary", sa.Text(), nullable=True),
        sa.Column("projects", sa.JSON(), nullable=False),
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
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_profiles_id"), "profiles", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_profiles_id"), table_name="profiles")
    op.drop_table("profiles")
