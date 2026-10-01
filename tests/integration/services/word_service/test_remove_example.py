"""Integration tests for WordService.remove_example.

Tests included:
    - test_remove_example_success: Verifies an example can be deleted.
"""

import pytest

from app.services.word_service import WordService


@pytest.mark.dictionary
def test_remove_example_success(session, make_word, make_source, make_example):
    """Verifies that remove_example deletes a contextual citation."""
    word = make_word(viet_word="học", english_translation="to learn")
    source = make_source(source_type="book", title="Book", url=None)
    example = make_example(word.id, source.id, "Tôi học.", "I learn.")
    session.flush()

    service = WordService(session)
    service.remove_example(example.id)
    loaded = service.get_entry(word.id)
    assert loaded.examples == []
