"""Integration tests for WordService.create_entry.

Tests included:
    - test_create_entry_rejects_invalid_words: Verifies blank and illegal characters fail.
    - test_create_entry_success_and_duplicate: Verifies create then duplicate rejection.
"""

import pytest

from app.exceptions import DictionaryValidationError, DictionaryWordDuplicateError
from app.services.word_service import WordService


@pytest.mark.dictionary
def test_create_entry_rejects_invalid_words(session):
    """Verifies that blank and non-Vietnamese characters are rejected on create."""
    service = WordService(session)
    with pytest.raises(DictionaryValidationError):
        service.create_entry("   ", "meaning")
    with pytest.raises(DictionaryValidationError):
        service.create_entry("abc123", "meaning")


@pytest.mark.dictionary
def test_create_entry_success_and_duplicate(session):
    """Verifies that a valid entry is created and duplicates raise DuplicateError."""
    service = WordService(session)
    created = service.create_entry("học tập", "to study", word_types=["verb"])
    assert created.viet_word == "học tập"
    assert "verb" in created.word_types
    with pytest.raises(DictionaryWordDuplicateError):
        service.create_entry("học tập", "again")
