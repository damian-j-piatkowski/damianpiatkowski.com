"""SQLAlchemy Core schema definition for the core dictionary_words table.

This module models the central relational anchor point for vocabulary tracking, 
maintaining lowercase unique constraints, modification audit trails, and prefix indexing.

Columns:
    id (Integer): Primary key with automatic incrementation.
    viet_word (String): Unique canonical lowercase Vietnamese script search string.
    english_translation (String): Core summary target translation string.
    created_at (TIMESTAMP): Timezone-aware creation tracking record (via Mixin).
    updated_at (TIMESTAMP): Timezone-aware modification tracking record (via Mixin).

Data Lifecycle Schema Examples:

    1. Required Insertion Payload:
       {
           "viet_word": "báo cáo",
           "english_translation": "to report; a report"
       }

    2. Resulting Complete Database Record:
       {
           "id": 201,
           "viet_word": "báo cáo",
           "english_translation": "to report; a report",
           "created_at": "2026-07-09T11:13:27Z",
           "updated_at": "2026-07-09T11:13:27Z"
       }
"""

from sqlalchemy import (
    Column,
    Index,
    Integer,
    String,
    Table
)

from app.models.base import metadata, TimestampMixin

dictionary_words = Table(
    'dictionary_words', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column(
        'viet_word',
        String(255, collation='utf8mb4_unicode_ci'),
        nullable=False,
        unique=True
    ),
    Column(
        'english_translation',
        String(500),
        nullable=False
    ),

    # Injects both 'created_at' and 'updated_at' via centralized TimestampMixin
    *TimestampMixin.modification_timestamps(),

    # Explicit Index for instant Autocomplete Prefix Queries
    Index('idx_viet_word_prefix', 'viet_word')
)
