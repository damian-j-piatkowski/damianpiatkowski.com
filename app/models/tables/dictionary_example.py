"""SQLAlchemy Core schema definition for the dictionary_examples table.

This module models the relational layer for contextual vocabulary usage exposures,
binding real-world language citations directly to their target dictionary keys 
alongside modification audit trails.

Columns:
    id (Integer): Primary key with automatic incrementation.
    word_id (Integer): Foreign key linking directly to the parent vocabulary word entry
        (dictionary_words.id) with cascading deletion.
    source_id (Integer): Foreign key linking to the origin documentation record
        (dictionary_sources.id) with cascading deletion.
    sentence (Text): The raw Vietnamese contextual text block supporting 'utf8mb4_unicode_ci'.
    english_translation (Text): The translated English meaning for parallel context matching.
    created_at (TIMESTAMP): The timezone-aware creation record (via Mixin).
    updated_at (TIMESTAMP): The timezone-aware active update tracking record (via Mixin).

Indices:
    idx_word_examples_lookup: A composite index built over (word_id, created_at) to accelerate
        historical context counts and chronological aggregate hydration routines.

Data Lifecycle Schema Examples:

    1. Required Insertion Payload:
       {
           "word_id": 88,
           "source_id": 14,
           "sentence": "Doraemon và nhóm bạn càng lúc càng gay cấn, các em đừng bỏ lỡ nhé!",
           "english_translation": "The adventures of Doraemon and his friends are getting more thrilling by the minute; don't miss out, kids!"
       }

    2. Resulting Complete Database Record:
       {
           "id": 504,
           "word_id": 88,
           "source_id": 14,
           "sentence": "Doraemon và nhóm bạn càng lúc càng gay cấn, các em đừng bỏ lỡ nhé!",
           "english_translation": "The adventures of Doraemon and his friends are getting more thrilling by the minute; don't miss out, kids!",
           "created_at": "2026-07-06T15:02:49Z",
           "updated_at": "2026-07-06T15:02:49Z"
       }
"""

from sqlalchemy import (
    Column,
    Integer,
    Table,
    Text,
    ForeignKey,
    Index
)

from app.models.base import metadata, TimestampMixin

dictionary_examples = Table(
    'dictionary_examples', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column(
        'word_id',
        Integer,
        ForeignKey('dictionary_words.id', ondelete='CASCADE'),
        nullable=False
    ),
    Column(
        'source_id',
        Integer,
        ForeignKey('dictionary_sources.id', ondelete='CASCADE'),
        nullable=False
    ),
    Column(
        'sentence',
        Text(collation='utf8mb4_unicode_ci'),
        nullable=False
    ),
    Column(
        'english_translation',
        Text(collation='utf8mb4_unicode_ci'),
        nullable=False
    ),

    # Injects both 'created_at' and 'updated_at' via centralized TimestampMixin
    *TimestampMixin.modification_timestamps(),

    Index('idx_word_examples_lookup', 'word_id', 'created_at')
)