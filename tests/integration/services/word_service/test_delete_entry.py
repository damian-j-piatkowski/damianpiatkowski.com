"""Integration tests for WordService.delete_entry.

Tests included:
    - test_delete_entry_cascades_associations: Verifies associations drop but roots remain.
"""

import pytest

from app.models.repositories.han_viet_repository import HanVietRepository
from app.services.word_service import WordService


@pytest.mark.dictionary
def test_delete_entry_cascades_associations(
        session, make_word, make_root, make_source, make_example, bind_word_type, bind_word_han_viet
):
    """Verifies that deleting a word removes associations but keeps Hán Việt roots."""
    word = make_word(viet_word="nghiên cứu", english_translation="research")
    root = make_root(root="cứu", chinese_character="究", root_meaning="research")
    source = make_source(source_type="book", title="Academic Source", url=None)
    make_example(word.id, source.id, "Tôi nghiên cứu.", "I research.")
    bind_word_type(word.id, "verb")
    bind_word_han_viet(word.id, root.id)
    session.flush()

    service = WordService(session)
    service.delete_entry(word.id)

    repo = HanVietRepository(session)
    assert repo.get_by_id(root.id).root == "cứu"
    assert repo.count_associations(root.id) == 0
