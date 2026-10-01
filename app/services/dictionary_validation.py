"""Dictionary word validation helpers."""

import re
from typing import Iterable, List

from app.domain.domain_enums import WordType
from app.exceptions import DictionaryValidationError

# Explicit Vietnamese alphabet (with diacritics), ASCII letters, spaces, hyphen.
_VIET_CHARS = (
    "aăâbcdđeêghiklmnoôơpqrstuưvxy"
    "áàảãạắằẳẵặấầẩẫậéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ"
)
_VIET_WORD_PATTERN = re.compile(
    rf"^[A-Za-z{_VIET_CHARS}{_VIET_CHARS.upper()}\s\-]+$",
    re.UNICODE,
)


def normalize_viet_word(viet_word: str) -> str:
    """Trim surrounding whitespace from a Vietnamese dictionary word."""
    return (viet_word or "").strip()


def validate_viet_word(viet_word: str) -> str:
    """Validate and normalize a Vietnamese dictionary word.

    Rules:
        - non-blank after trim
        - only Vietnamese letters (including diacritics), spaces, and hyphen
    """
    normalized = normalize_viet_word(viet_word)
    if not normalized:
        raise DictionaryValidationError(
            "Dictionary word cannot be blank.",
            field="viet_word",
        )
    if not _VIET_WORD_PATTERN.match(normalized):
        raise DictionaryValidationError(
            "Dictionary word may only contain Vietnamese letters, spaces, and hyphens.",
            field="viet_word",
        )
    return normalized


def validate_english_translation(english_translation: str) -> str:
    """Require a non-blank English translation."""
    normalized = (english_translation or "").strip()
    if not normalized:
        raise DictionaryValidationError(
            "English translation is required.",
            field="english_translation",
        )
    return normalized


def validate_word_types(word_types: Iterable[str] | None) -> List[str]:
    """Validate grammatical type values against the WordType enum."""
    if not word_types:
        return []
    allowed = {member.value for member in WordType}
    validated: List[str] = []
    for raw in word_types:
        value = (raw or "").strip().lower()
        if value not in allowed:
            raise DictionaryValidationError(
                f"Unsupported word type '{raw}'.",
                field="word_types",
            )
        if value not in validated:
            validated.append(value)
    return validated
