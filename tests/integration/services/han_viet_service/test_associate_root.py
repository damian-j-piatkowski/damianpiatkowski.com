"""Integration tests for HanVietService.associate_root.

Tests included:
    - test_associate_root_success: Verifies linking an existing root to a word.
"""

import pytest

from app.services.han_viet_service import HanVietService


@pytest.mark.dictionary
def test_associate_root_success(session, make_word, make_root):
    """Verifies that associate_root links an existing root to a dictionary word."""
    word = make_word(viet_word="học", english_translation="to learn")
    root = make_root(root="học", chinese_character="學", root_meaning="study")
    session.flush()

    service = HanVietService(session)
    service.associate_root(word.id, root.id)
    assert service.roots.count_associations(root.id) == 1
