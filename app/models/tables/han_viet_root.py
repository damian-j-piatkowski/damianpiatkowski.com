"""SQLAlchemy Core schema definition for the han_viet_roots table.

This module models the relational layer for Chinese structural semantic root
components (Hán Việt), mapping linguistic sub-patterns to their base definitions.

Columns:
    id (Integer): Primary key with automatic incrementation.
    root (String): The unique lowercase alphanumeric string representing the Vietnamese root spelling.
    chinese_character (String): Mandatory traditional/simplified Hanzi logogram representation.
    root_meaning (String): The core English semantic translation definition of the component.

Data Lifecycle Schema Examples:

    1. Required Insertion Payload:
       {
           "root": "bản",
           "chinese_character": "本",
           "root_meaning": "root, basis, foundation"
       }

    2. Resulting Complete Database Record:
       {
           "id": 42,
           "root": "bản",
           "chinese_character": "本",
           "root_meaning": "root, basis, foundation"
       }
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Table
)

from app.models.base import metadata

han_viet_roots = Table(
    'han_viet_roots', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column(
        'root',
        String(50, collation='utf8mb4_unicode_ci'),
        nullable=False,
        unique=True
    ),
    Column(
        'chinese_character',
        String(10, collation='utf8mb4_unicode_ci'),
        nullable=False
    ),
    Column(
        'root_meaning',
        String(255),
        nullable=False
    )
)
