"""add workload revision

Revision ID: 8e9dbacb38ff
Revises: f803f250638a
Create Date: 2026-08-02 13:35:17.362121

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "8e9dbacb38ff"
down_revision: str | Sequence[str] | None = "f803f250638a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "workload_revision",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("workload_id", sa.Integer(), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("image", sa.String(length=255), nullable=False),
        sa.Column("cpu_limit", sa.Numeric(precision=6, scale=3), nullable=True),
        sa.Column("memory_limit", sa.BigInteger(), nullable=True),
        sa.Column("spec", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("workload_id", "revision", name="uq_workload_revision"),
    )
    op.create_index(
        "ix_workload_revision_workload_id",
        "workload_revision",
        ["workload_id"],
        unique=False,
    )
    op.add_column(
        "workload",
        sa.Column("current_revision_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "container",
        sa.Column("revision_id", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("container", "revision_id")
    op.drop_column("workload", "current_revision_id")
    op.drop_index("ix_workload_revision_workload_id", table_name="workload_revision")
    op.drop_table("workload_revision")
