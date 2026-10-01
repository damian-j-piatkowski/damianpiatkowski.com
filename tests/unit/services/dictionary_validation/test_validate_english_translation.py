"""Unit tests for dictionary_validation.validate_english_translation.

Tests included:
    - test_validate_english_translation_accepts_trimmed_text: Verifies non-blank translations.
    - test_validate_english_translation_rejects_blank: Verifies blank rejection and field name.
"""

import pytest

from app.exceptions import DictionaryValidationError
from app.services.dictionary_validation import validate_english_translation


@pytest.mark.dictionary
@pytest.mark.parametrize(
    "raw,expected",
    [
        ("  to study  ", "to study"),
        ("freedom", "freedom"),
        ("a report; to report", "a report; to report"),
    ],
)
def test_validate_english_translation_accepts_trimmed_text(raw, expected):
    """Verifies that non-blank English translations are trimmed and returned."""
    assert validate_english_translation(raw) == expected


@pytest.mark.dictionary
@pytest.mark.parametrize("raw", ["", "   ", None])
def test_validate_english_translation_rejects_blank(raw):
    """Verifies that blank English translations raise with field english_translation."""
    with pytest.raises(DictionaryValidationError) as exc_info:
        validate_english_translation(raw)
    assert exc_info.value.field == "english_translation"
