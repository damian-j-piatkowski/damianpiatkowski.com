"""Unit tests for dictionary_validation.validate_viet_word.

Tests included:
    - test_validate_viet_word_accepts_valid_input: Verifies accepted Vietnamese forms.
    - test_validate_viet_word_rejects_invalid_input: Verifies rejection and field name.
"""

import pytest

from app.exceptions import DictionaryValidationError
from app.services.dictionary_validation import validate_viet_word


@pytest.mark.dictionary
@pytest.mark.parametrize(
    "raw,expected",
    [
        ("  báo cáo  ", "báo cáo"),
        ("nghiệm", "nghiệm"),
        ("học-tập", "học-tập"),
        ("Ăn quả", "Ăn quả"),
    ],
)
def test_validate_viet_word_accepts_valid_input(raw, expected):
    """Verifies that valid Vietnamese letters, spaces, and hyphens are accepted."""
    assert validate_viet_word(raw) == expected


@pytest.mark.dictionary
@pytest.mark.parametrize(
    "raw",
    ["", "   ", "hello123", "báo!", "word_with_underscore", "ok?"],
)
def test_validate_viet_word_rejects_invalid_input(raw):
    """Verifies that invalid dictionary words raise DictionaryValidationError on viet_word."""
    with pytest.raises(DictionaryValidationError) as exc_info:
        validate_viet_word(raw)
    assert exc_info.value.field == "viet_word"
