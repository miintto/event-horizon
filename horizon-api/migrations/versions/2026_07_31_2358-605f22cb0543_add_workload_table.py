"""add workload table

Revision ID: 605f22cb0543
Revises: 9dbc427e1870
Create Date: 2026-07-31 23:58:49.615830

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "605f22cb0543"
down_revision: str | Sequence[str] | None = "9dbc427e1870"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "workload",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=512), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="uq_workload_name"),
    )
    op.add_column(
        "container",
        sa.Column("workload_id", sa.Integer(), nullable=True),
    )
    op.create_index(
        "ix_container_workload_id",
        "container",
        ["workload_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_container_workload_id", table_name="container")
    op.drop_column("container", "workload_id")
    op.drop_table("workload")
