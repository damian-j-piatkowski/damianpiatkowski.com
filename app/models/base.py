"""Centralized metadata registry and shared tracking foundations for the database layer.

This module provides a single shared MetaData instance used to collect, bind,
and cross-reference all database table architectures across the application,
ensuring clean foreign key resolution and unified migration tracking.

Importing this module automatically triggers the registration of all table schemas
by importing the `app.models.tables` package, guaranteeing complete target metadata
visibility for Alembic migration autogeneration.

Additionally, it houses reusable structural utilities to enforce auditing consistency
across individual schema definitions.

Classes:
    TimestampMixin: Injects explicit MySQL-compatible temporal tracking columns.
"""

from sqlalchemy import (
    MetaData,
    Column,
    TIMESTAMP,
    text,
    FetchedValue
)

# Shared metadata catalog tracking all core table schemas
metadata = MetaData()


class TimestampMixin:
    """Provides standardized creation and modification tracking columns for Core Tables.
    
    Exposes declarative factory initializers designed to seamlessly integrate native
    MySQL timezone-aware TIMESTAMP patterns into standard procedural Table setups.
    """

    @classmethod
    def creation_timestamp(cls) -> Column:
        """Generates a standardized read-only record initialization timestamp.

        Returns:
            Column: Pre-configured timezone-aware record generation tracker.
        """
        return Column(
            'created_at',
            TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text('CURRENT_TIMESTAMP')
        )

    @classmethod
    def modification_timestamps(cls) -> tuple[Column, Column]:
        """Generates paired tracking columns for both creation and updates.

        Returns:
            tuple[Column, Column]: Dual created_at and reactive updated_at schema columns.
        """
        created = cls.creation_timestamp()
        updated = Column(
            'updated_at',
            TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text('CURRENT_TIMESTAMP'),
            server_onupdate=FetchedValue()
        )
        return created, updated

# Import the tables package to register all schema modules into `metadata`
import app.models.tables  # noqa: F401
