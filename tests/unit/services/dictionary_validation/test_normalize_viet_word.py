"""Unit tests for dictionary_validation.normalize_viet_word.

Tests included:
    - test_normalize_viet_word_trims_and_handles_blank: Verifies trim and blank handling.
"""

import pytest

from app.services.dictionary_validation import normalize_viet_word


@pytest.mark.dictionary
@pytest.mark.parametrize(
    "raw,expected",
    [
        ("  báo cáo  ", "báo cáo"),
        ("nghiệm", "nghiệm"),
        ("", ""),
        ("   ", ""),
        (None, ""),
    ],
)
def test_normalize_viet_word_trims_and_handles_blank(raw, expected):
    """Verifies that normalize_viet_word trims whitespace and treats blank input as empty."""
    assert normalize_viet_word(raw) == expected
