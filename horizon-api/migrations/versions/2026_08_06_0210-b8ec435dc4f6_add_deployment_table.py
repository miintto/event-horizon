"""add deployment table

Revision ID: b8ec435dc4f6
Revises: 2294cfc4c029
Create Date: 2026-08-06 02:10:36.991061

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b8ec435dc4f6"
down_revision: str | Sequence[str] | None = "2294cfc4c029"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "deployment",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("host_id", sa.Integer(), nullable=False),
        sa.Column("workload_id", sa.Integer(), nullable=False),
        sa.Column("revision_id", sa.Integer(), nullable=False),
        sa.Column("container_id", sa.Integer(), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "PENDING",
                "RUNNING",
                "SUCCEEDED",
                "FAILED",
                name="deploymentstatus",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("error_message", sa.String(length=500), nullable=True),
        sa.Column("claimed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_deployment_host_status", "deployment", ["host_id", "status"], unique=False
    )
    op.create_index(
        "ix_deployment_workload_id", "deployment", ["workload_id"], unique=False
    )
    op.create_index(
        "uq_deployment_active",
        "deployment",
        ["workload_id"],
        unique=True,
        postgresql_where=sa.text("status IN ('PENDING', 'RUNNING')"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("uq_deployment_active", table_name="deployment")
    op.drop_index("ix_deployment_workload_id", table_name="deployment")
    op.drop_index("ix_deployment_host_status", table_name="deployment")
    op.drop_table("deployment")
