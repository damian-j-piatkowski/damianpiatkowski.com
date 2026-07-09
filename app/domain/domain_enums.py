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


class WordType(StrEnum):
    """Grammatical classifications for Vietnamese dictionary entries.
    
    Members are explicitly mapped to standard string keys for storage layer 
    isolation, featuring contextual cross-linguistic translations and target examples.
    """
    NOUN = "noun"  # Danh từ (e.g., "báo cáo" - report, "thành phố" - city)
    VERB = "verb"  # Động từ (e.g., "báo cáo" - to report, "đặt" - to place/order)
    ADJECTIVE = "adjective"  # Tính từ (e.g., "nhanh" - fast, "đẹp" - beautiful)
    ADVERB = "adverb"  # Phó từ / Trạng từ (e.g., "rất" - very, "luôn luôn" - always)
    PRONOUN = "pronoun"  # Đại từ (e.g., "tôi" - I, "bạn" - you)
    PREPOSITION = "preposition"  # Giới từ (e.g., "ở" - at/in, "trên" - on)
    CONJUNCTION = "conjunction"  # Liên từ (e.g., "và" - and, "nhưng" - but)
    PARTICLE = "particle"  # Trợ từ / Thán từ (e.g., "à" - emphasis particle, "nhé" - gentle suggestion)
    IDIOM = "idiom"  # Thành ngữ (e.g., "Mẹ tròn con vuông" - smooth childbirth, "Mưa dầm thấm lâu")
    PROVERB = "proverb"  # Tục ngữ (e.g., "Ăn quả nhớ kẻ trồng cây" - gratitude reminder)
