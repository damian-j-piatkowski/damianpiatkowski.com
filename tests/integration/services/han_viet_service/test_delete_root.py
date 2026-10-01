"""Integration tests for HanVietService.unlink_root and delete_root.

Tests included:
    - test_unlink_then_delete_root: Verifies in-use block, unlink, then delete.
"""

import pytest

from app.exceptions import HanVietRootInUseError
from app.models.tables.han_viet_root import han_viet_roots
from app.services.han_viet_service import HanVietService


@pytest.mark.dictionary
def test_unlink_then_delete_root(session, make_word, make_root, bind_word_han_viet):
    """Verifies that delete_root is blocked while associations remain, then succeeds."""
    word = make_word(viet_word="nhân viên", english_translation="employee")
    root = make_root(root="nhân", chinese_character="人", root_meaning="person")
    bind_word_han_viet(word.id, root.id)
    session.flush()

    service = HanVietService(session)
    with pytest.raises(HanVietRootInUseError):
        service.delete_root(root.id)

    service.unlink_root(word.id, root.id)
    service.delete_root(root.id)

    remaining_roots = session.execute(han_viet_roots.select()).fetchall()
    assert all(row.id != root.id for row in remaining_roots)
