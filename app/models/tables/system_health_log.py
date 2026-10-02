"""SQLAlchemy Core schema for system_health_logs.

Stores 15-minute node metric snapshots for admin trend charts and alert cooldown.
"""

from sqlalchemy import (
    Boolean,
    Column,
    Float,
    Index,
    Integer,
    Table,
    TIMESTAMP,
    text,
)

from app.models.base import metadata

system_health_logs = Table(
    "system_health_logs",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column(
        "timestamp",
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    ),
    Column("cpu_percent", Float, nullable=False),
    Column("ram_percent", Float, nullable=False),
    Column("ram_used_mb", Float, nullable=False),
    Column("swap_percent", Float, nullable=False),
    Column("disk_percent", Float, nullable=False),
    Column(
        "alert_sent",
        Boolean,
        nullable=False,
        server_default=text("0"),
    ),
    Index("idx_system_health_logs_timestamp", "timestamp"),
)
