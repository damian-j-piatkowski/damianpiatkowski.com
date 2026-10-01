"""Integration tests for WordService.check_duplicate.

Tests included:
    - test_check_duplicate_finds_existing: Verifies an existing word is returned.
    - test_check_duplicate_blank_returns_none: Verifies blank input yields None.
"""

import pytest

from app.services.word_service import WordService


@pytest.mark.dictionary
def test_check_duplicate_finds_existing(session):
    """Verifies that check_duplicate returns the existing word when present."""
    service = WordService(session)
    service.create_entry("học tập", "to study")
    found = service.check_duplicate("học tập")
    assert found is not None
    assert found.viet_word == "học tập"


@pytest.mark.dictionary
def test_check_duplicate_blank_returns_none(session):
    """Verifies that blank queries return None without querying the database."""
    service = WordService(session)
    assert service.check_duplicate("   ") is None
    assert service.check_duplicate("") is None
