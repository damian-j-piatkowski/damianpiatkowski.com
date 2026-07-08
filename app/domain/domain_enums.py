"""Defines strict domain enumeration constraints across the system.

This module houses centralized, iterable string enumerations used to enforce data
integrity, type-safety, and automatic dropdown generation inside web forms.
"""

from enum import StrEnum


class SourceType(StrEnum):
    """Supported classification profiles for dictionary example context origins."""
    BOOK = "book"
    MANGA = "manga"
    ARTICLE = "article"
    OTHER = "other"
