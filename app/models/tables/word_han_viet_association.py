"""SQLAlchemy Core schema definition for the word_han_viet_association table.

This module models the clean relational junction bridge table facilitating a
many-to-many relationship between dictionary words and their component Hán Việt semantic roots.

Columns:
    word_id (Integer): Foreign key bound to the target dictionary word record. Part of the composite primary key.
    root_id (Integer): Foreign key bound to the contributing Hán Việt root record. Part of the composite primary key.

Data Lifecycle Schema Examples:

    Linguistic Mapping Context:
        - Word ID 101: "phương pháp" (Method)
        - Word ID 102: "phương hướng" (Direction)
        - Root ID 42:  "phương" (方 - direction/method)
        - Root ID 43:  "pháp" (法 - law/rule)
        - Root ID 44:  "hướng" (向 - to face/direction)

    1. Required Insertion Payloads (Mapping components for "phương pháp"):
       [
           {"word_id": 101, "root_id": 42},
           {"word_id": 101, "root_id": 43}
       ]

    2. Resulting Complete Database Records (The entire cross-link map for both words):
       [
           {"word_id": 101, "root_id": 42},  # links "phương pháp" -> "phương"
           {"word_id": 101, "root_id": 43},  # links "phương pháp" -> "pháp"
           {"word_id": 102, "root_id": 42},  # links "phương hướng" -> "phương"
           {"word_id": 102, "root_id": 44}   # links "phương hướng" -> "hướng"
       ]
"""

from sqlalchemy import (
    Column,
    Integer,
    Table,
    ForeignKey
)

from app.models.base import metadata

word_han_viet_association = Table(
    'word_han_viet_association', metadata,
    Column(
        'word_id',
        Integer,
        ForeignKey('dictionary_words.id', ondelete='CASCADE'),
        primary_key=True
    ),
    Column(
        'root_id',
        Integer,
        ForeignKey('han_viet_roots.id', ondelete='CASCADE'),
        primary_key=True
    )
)