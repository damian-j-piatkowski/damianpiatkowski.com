"""add_system_health_logs

Revision ID: c8d4f0b23e15
Revises: b7c3e9a12f04
Create Date: 2026-10-01 22:00:00.000000

Adds system_health_logs for 15-minute node metric snapshots used by the
admin System Health live and trends views.
"""

from alembic import op
import sqlalchemy as sa


revision = "c8d4f0b23e15"
down_revision = "b7c3e9a12f04"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "system_health_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "timestamp",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("cpu_percent", sa.Float(), nullable=False),
        sa.Column("ram_percent", sa.Float(), nullable=False),
        sa.Column("ram_used_mb", sa.Float(), nullable=False),
        sa.Column("swap_percent", sa.Float(), nullable=False),
        sa.Column("disk_percent", sa.Float(), nullable=False),
        sa.Column(
            "alert_sent",
            sa.Boolean(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_system_health_logs_timestamp",
        "system_health_logs",
        ["timestamp"],
        unique=False,
    )


def downgrade():
    op.drop_index("idx_system_health_logs_timestamp", table_name="system_health_logs")
    op.drop_table("system_health_logs")
