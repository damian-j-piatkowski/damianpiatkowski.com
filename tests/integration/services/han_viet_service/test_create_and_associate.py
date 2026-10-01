"""Integration tests for HanVietService.create_and_associate.

Tests included:
    - test_create_and_associate_success: Verifies root creation and association.
"""

import pytest

from app.models.tables.word_han_viet_association import word_han_viet_association
from app.services.han_viet_service import HanVietService


@pytest.mark.dictionary
def test_create_and_associate_success(session, make_word):
    """Verifies that create_and_associate inserts a root and links it to a word."""
    word = make_word(viet_word="chính trị", english_translation="politics")
    session.flush()

    service = HanVietService(session)
    created = service.create_and_associate(
        word_id=word.id,
        root="chính",
        chinese_character="政",
        root_meaning="politics",
    )

    associations = session.execute(
        word_han_viet_association.select().where(
            word_han_viet_association.c.word_id == word.id,
            word_han_viet_association.c.root_id == created.id,
        )
    ).fetchall()
    assert len(associations) == 1
