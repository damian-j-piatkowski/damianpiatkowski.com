"""Integration tests for WordService.search_prefix.

Tests included:
    - test_search_prefix_matches: Verifies prefix matches are returned.
    - test_search_prefix_empty_query: Verifies empty query returns [].
"""

import pytest

from app.services.word_service import WordService


@pytest.mark.dictionary
def test_search_prefix_matches(session, make_word):
    """Verifies that search_prefix returns words matching the Vietnamese prefix."""
    make_word(viet_word="bàn học", english_translation="study desk")
    make_word(viet_word="bàn ăn", english_translation="dining table")
    make_word(viet_word="ghế", english_translation="chair")
    session.flush()

    service = WordService(session)
    results = service.search_prefix("bàn")
    words = {word.viet_word for word in results}
    assert "bàn học" in words
    assert "bàn ăn" in words
    assert "ghế" not in words


@pytest.mark.dictionary
def test_search_prefix_empty_query(session, make_word):
    """Verifies that an empty prefix returns an empty list."""
    make_word(viet_word="bàn", english_translation="table")
    session.flush()
    service = WordService(session)
    assert service.search_prefix("   ") == []
