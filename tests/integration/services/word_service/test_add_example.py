"""Integration tests for WordService.add_example.

Tests included:
    - test_add_example_success: Verifies an example is attached to a word.
    - test_add_example_rejects_blank_sentence: Verifies blank sentence validation.
"""

import pytest

from app.exceptions import DictionaryValidationError
from app.services.word_service import WordService


@pytest.mark.dictionary
def test_add_example_success(session, make_word, make_source):
    """Verifies that add_example creates a contextual citation for a word."""
    word = make_word(viet_word="học", english_translation="to learn")
    source = make_source(source_type="book", title="Book", url=None)
    session.flush()

    service = WordService(session)
    example = service.add_example(
        word.id,
        source.id,
        "Tôi học mỗi ngày.",
        "I study every day.",
    )
    assert example.word_id == word.id
    assert example.sentence == "Tôi học mỗi ngày."


@pytest.mark.dictionary
def test_add_example_rejects_blank_sentence(session, make_word, make_source):
    """Verifies that a blank example sentence raises DictionaryValidationError."""
    word = make_word(viet_word="học", english_translation="to learn")
    source = make_source(source_type="book", title="Book", url=None)
    session.flush()

    service = WordService(session)
    with pytest.raises(DictionaryValidationError) as exc_info:
        service.add_example(word.id, source.id, "  ", "translation")
    assert exc_info.value.field == "sentence"
