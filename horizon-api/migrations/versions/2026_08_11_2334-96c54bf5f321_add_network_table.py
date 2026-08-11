"""add network table

Revision ID: 96c54bf5f321
Revises: b8ec435dc4f6
Create Date: 2026-08-11 23:34:20.281110

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "96c54bf5f321"
down_revision: str | Sequence[str] | None = "b8ec435dc4f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "network",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column(
            "driver", sa.String(length=50), server_default="bridge", nullable=False
        ),
        sa.Column(
            "options",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="{}",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="uq_network_name"),
    )
    op.create_table(
        "workload_network",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("workload_id", sa.Integer(), nullable=False),
        sa.Column("network_id", sa.Integer(), nullable=False),
        sa.Column("alias", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("workload_id", "network_id", name="uq_workload_network"),
    )
    op.create_index(
        "ix_workload_network_network_id",
        "workload_network",
        ["network_id"],
        unique=False,
    )
    op.create_table(
        "network_host_state",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("network_id", sa.Integer(), nullable=False),
        sa.Column("host_id", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("SYNCED", "FAILED", name="networksyncstatus", native_enum=False),
            nullable=False,
        ),
        sa.Column("error_message", sa.String(length=1024), nullable=True),
        sa.Column("synced_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("network_id", "host_id", name="uq_network_host_state"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("network_host_state")
    op.drop_index("ix_workload_network_network_id", table_name="workload_network")
    op.drop_table("workload_network")
    op.drop_table("network")
