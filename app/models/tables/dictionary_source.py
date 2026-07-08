"""SQLAlchemy Core schema definition for the dictionary_sources table.

This module models the relational layer for origin tracking documentation, mapping
where contextual vocabulary usage expressions were mined (e.g., news articles, literature).

Columns:
    id (Integer): Primary key with automatic incrementation.
    source_type (String): Categorical string bounded to valid SourceType enum keys.
    title (String): The descriptive name or headline of the origin publication text block.
    url (String): Optional remote URL path link pointing back to the digitized media.
    created_at (TIMESTAMP): The timezone-aware creation record, defaulting to database time.

Indices:
    idx_sources_type_lookup: A clean lookup index built over (source_type) to optimize
        analytical aggregation filtering loops across differing media mediums.

Data Lifecycle Schema Examples:

    Scenario A: Physical Media (Omit optional URL field)

        1. Required Insertion Payload:
           {
               "source_type": "book",
               "title": "21 bài học cho thế kỷ 21"
           }

        2. Resulting Complete Database Record:
           {
               "id": 12,
               "source_type": "book",
               "title": "21 bài học cho thế kỷ 21",
               "url": None,
               "created_at": datetime.datetime(2026, 7, 8, 5, 20, 0, tzinfo=datetime.timezone.utc)
           }

    Scenario B: Digital Media (Include required URL field)

        1. Required Insertion Payload:
           {
               "source_type": "article",
               "title": "VnExpress - Messi điều chỉnh thế nào để giúp Argentina thắng ngược Ai Cập?",
               "url": "https://vnexpress.net/messi-dieu-chinh-the-nao-de-giup-argentina-thang-nguoc-ai-cap-5094933.html"
           }

        2. Resulting Complete Database Record:
           {
               "id": 14,
               "source_type": "article",
               "title": "VnExpress - Messi điều chỉnh thế nào để giúp Argentina thắng ngược Ai Cập?",
               "url": "https://vnexpress.net/messi-dieu-chinh-the-nao-de-giup-argentina-thang-nguoc-ai-cap-5094933.html",
               "created_at": datetime.datetime(2026, 7, 8, 5, 25, 0, tzinfo=datetime.timezone.utc)
           }
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Table,
    TIMESTAMP,
    Index,
    text
)

from app.models.base import metadata

dictionary_sources = Table(
    'dictionary_sources', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column(
        'source_type',
        String(32),  # Validated and bounded exclusively via Python application logic
        nullable=False
    ),
    Column(
        'title',
        String(255, collation='utf8mb4_unicode_ci'),
        nullable=False
    ),
    Column(
        'url',
        String(2048),
        nullable=True
    ),
    Column(
        'created_at',
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP')
    ),

    Index('idx_sources_type_lookup', 'source_type')
)
