"""SQLAlchemy Core schema definition for the word_type_association table.

This module models the relational junction bridge table facilitating a
many-to-many relationship between dictionary words and their grammatical classifications.

Columns:
    word_id (Integer): Foreign key bound to the target dictionary word record. Part of the composite primary key.
    word_type (String): Categorical string representing the assigned grammatical type. Part of the composite primary key.

Data Lifecycle Schema Examples:

    Linguistic Mapping Context (Omnipredicativity Case Study):
        - Word ID 201: "báo cáo"

    1. Required Insertion Payloads (Mapping "báo cáo" as both a Noun and a Verb):
       [
           {"word_id": 201, "word_type": "noun"},
           {"word_id": 201, "word_type": "verb"}
       ]

    2. Resulting Complete Database Records:
       [
           {"word_id": 201, "word_type": "noun"},
           {"word_id": 201, "word_type": "verb"}
       ]
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Table,
    ForeignKey
)

from app.models.base import metadata

word_type_association = Table(
    'word_type_association', metadata,
    Column(
        'word_id',
        Integer,
        ForeignKey('dictionary_words.id', ondelete='CASCADE'),
        primary_key=True
    ),
    Column(
        'word_type',
        String(32),  # Validated and bounded strictly via Python application logic
        primary_key=True
    )
)