"""Integration tests for WordService.get_entry.

Tests included:
    - test_get_entry_loads_relations: Verifies types, examples, and roots hydrate.
    - test_get_entry_missing_raises: Verifies unknown id raises NotFoundError.
"""

import pytest

from app.exceptions import DictionaryWordNotFoundError
from app.services.word_service import WordService


@pytest.mark.dictionary
def test_get_entry_loads_relations(
        session, make_word, make_root, make_source, make_example, bind_word_type, bind_word_han_viet
):
    """Verifies that get_entry returns a word with hydrated relationships."""
    word = make_word(viet_word="học tập", english_translation="to study")
    root = make_root(root="học", chinese_character="學", root_meaning="study")
    source = make_source(source_type="book", title="Source", url=None)
    make_example(word.id, source.id, "Tôi học tập.", "I study.")
    bind_word_type(word.id, "verb")
    bind_word_han_viet(word.id, root.id)
    session.flush()

    service = WordService(session)
    loaded = service.get_entry(word.id)
    assert loaded.viet_word == "học tập"
    assert "verb" in loaded.word_types
    assert len(loaded.examples) == 1
    assert len(loaded.han_viet_roots) == 1


@pytest.mark.dictionary
def test_get_entry_missing_raises(session):
    """Verifies that an unknown word id raises DictionaryWordNotFoundError."""
    service = WordService(session)
    with pytest.raises(DictionaryWordNotFoundError):
        service.get_entry(999999)
