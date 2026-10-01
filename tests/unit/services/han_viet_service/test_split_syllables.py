"""Unit tests for han_viet_service.split_syllables.

Tests included:
    - test_split_syllables_preserves_diacritics: Verifies whitespace split keeps diacritics.
"""

import pytest

from app.services.han_viet_service import split_syllables


@pytest.mark.dictionary
@pytest.mark.parametrize(
    "raw,expected",
    [
        ("chính trị", ["chính", "trị"]),
        ("nghiệm", ["nghiệm"]),
        ("  học   tập ", ["học", "tập"]),
    ],
)
def test_split_syllables_preserves_diacritics(raw, expected):
    """Verifies that split_syllables tokenizes on whitespace while preserving diacritics."""
    assert split_syllables(raw) == expected
