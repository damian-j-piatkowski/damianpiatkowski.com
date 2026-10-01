"""Integration tests for WordService.get_public_entry.

Tests included:
    - test_get_public_entry_orders_etymology: Verifies syllable-ordered etymology.
    - test_get_public_entry_missing_raises: Verifies unknown id raises NotFoundError.
"""

import pytest

from app.exceptions import DictionaryWordNotFoundError
from app.services.word_service import WordService


@pytest.mark.dictionary
def test_get_public_entry_orders_etymology(
        session, make_word, make_root, bind_word_han_viet
):
    """Verifies that public entry etymology follows viet_word syllable order."""
    word = make_word(viet_word="chính trị", english_translation="politics")
    root_tri = make_root(root="trị", chinese_character="治", root_meaning="govern")
    root_chinh = make_root(root="chính", chinese_character="正", root_meaning="main")
    # Associate in reverse order to prove sorting is syllable-based.
    bind_word_han_viet(word.id, root_tri.id)
    bind_word_han_viet(word.id, root_chinh.id)
    session.flush()

    service = WordService(session)
    payload = service.get_public_entry(word.id)
    assert payload["word"].id == word.id
    roots = [item["root"] for item in payload["ordered_etymology"]]
    assert roots == ["chính", "trị"]


@pytest.mark.dictionary
def test_get_public_entry_missing_raises(session):
    """Verifies that an unknown word id raises DictionaryWordNotFoundError."""
    service = WordService(session)
    with pytest.raises(DictionaryWordNotFoundError):
        service.get_public_entry(999999)
