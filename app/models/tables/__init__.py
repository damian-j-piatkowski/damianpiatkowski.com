"""Centralized export interface and discovery hub for all table schemas.

This module exposes every individual SQLAlchemy Core Table instance across the
application schema layer.

Why this package module exists:
--------------------------------
1. Centralized Schema Discovery:
   Importing this package executes each child schema module, attaching every Table
   instance to the shared `metadata` registry defined in `app.models.base`. This
   guarantees Alembic autogeneration detects all tables during migrations without
   requiring explicit imports across multiple files.

2. Clean Export Namespace:
   Provides a clean, single-import interface for the ORM mapper registry (`app.orm`)
   and database initialization utilities.
"""

from app.models.tables.blog_post import blog_posts
from app.models.tables.dictionary_example import dictionary_examples
from app.models.tables.dictionary_source import dictionary_sources
from app.models.tables.dictionary_word import dictionary_words
from app.models.tables.han_viet_root import han_viet_roots
from app.models.tables.user import users
from app.models.tables.word_han_viet_association import word_han_viet_association
from app.models.tables.word_type_association import word_type_association

__all__ = [
    "blog_posts",
    "dictionary_examples",
    "dictionary_sources",
    "dictionary_words",
    "han_viet_roots",
    "users",
    "word_han_viet_association",
    "word_type_association",
]
