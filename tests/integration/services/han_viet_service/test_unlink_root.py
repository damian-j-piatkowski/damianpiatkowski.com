"""Integration tests for HanVietService.unlink_root.

Tests included:
    - test_unlink_root_clears_association: Verifies association removal only.
"""

import pytest

from app.services.han_viet_service import HanVietService


@pytest.mark.dictionary
def test_unlink_root_clears_association(session, make_word, make_root, bind_word_han_viet):
    """Verifies that unlink_root removes the association while keeping the root."""
    word = make_word(viet_word="học", english_translation="to learn")
    root = make_root(root="học", chinese_character="學", root_meaning="study")
    bind_word_han_viet(word.id, root.id)
    session.flush()

    service = HanVietService(session)
    service.unlink_root(word.id, root.id)
    assert service.roots.count_associations(root.id) == 0
    assert service.roots.get_by_id(root.id).root == "học"
