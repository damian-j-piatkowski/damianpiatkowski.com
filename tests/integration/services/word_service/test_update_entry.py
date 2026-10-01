"""Integration tests for WordService.update_entry.

Tests included:
    - test_update_entry_fields_and_types: Verifies field and type updates.
"""

import pytest

from app.services.word_service import WordService


@pytest.mark.dictionary
def test_update_entry_fields_and_types(session, make_word, bind_word_type):
    """Verifies that update_entry changes translation and word types."""
    word = make_word(viet_word="bàn", english_translation="table")
    bind_word_type(word.id, "noun")
    session.flush()

    service = WordService(session)
    updated = service.update_entry(
        word.id,
        english_translation="desk",
        word_types=["noun", "verb"],
    )
    assert updated.english_translation == "desk"
    assert set(updated.word_types) == {"noun", "verb"}
