"""Integration tests for the word_han_viet_association junction table schema.

This module validates many-to-many bridge constraints, composite primary key uniqueness,
and cascade isolation behaviors across vocabulary words and Hán Việt root syllables.
"""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.tables.dictionary_word import dictionary_words
from app.models.tables.han_viet_root import han_viet_roots
from app.models.tables.word_han_viet_association import word_han_viet_association


@pytest.mark.dictionary
def test_word_han_viet_association_cascade_on_word_deletion(session: Session, seed_dictionary):
    """Verifies that deleting a dictionary word cleans up the bridge rows without affecting the linked Hán Việt roots."""
    data = seed_dictionary()
    word_to_delete = data["words"][0]  # "học tập"
    root_to_check = data["roots"][0]  # "học"

    # Delete the target word
    session.execute(
        dictionary_words.delete().where(dictionary_words.c.id == word_to_delete.id)
    )
    session.commit()

    # Assert: Bridge rows for the deleted word have been purged
    bridge_rows = session.execute(
        word_han_viet_association.select().where(word_han_viet_association.c.word_id == word_to_delete.id)
    ).fetchall()
    assert len(bridge_rows) == 0

    # Assert: Core HanVietRoot record remains untouched
    root_exists = session.execute(
        han_viet_roots.select().where(han_viet_roots.c.id == root_to_check.id)
    ).fetchone()
    assert root_exists is not None


@pytest.mark.dictionary
def test_word_han_viet_association_cascade_on_root_deletion(session: Session, seed_dictionary):
    """Verifies that deleting a Hán Việt root cleans up the bridge rows without affecting the linked dictionary words."""
    data = seed_dictionary()
    root_to_delete = data["roots"][2]  # "nhân"
    word_to_check = data["words"][1]  # "nhân viên"

    # Delete the target root
    session.execute(
        han_viet_roots.delete().where(han_viet_roots.c.id == root_to_delete.id)
    )
    session.commit()

    # Assert: Bridge rows linking to the deleted root are gone
    bridge_rows = session.execute(
        word_han_viet_association.select().where(word_han_viet_association.c.root_id == root_to_delete.id)
    ).fetchall()
    assert len(bridge_rows) == 0

    # Assert: Core DictionaryWord entry is preserved
    word_exists = session.execute(
        dictionary_words.select().where(dictionary_words.c.id == word_to_check.id)
    ).fetchone()
    assert word_exists is not None


@pytest.mark.dictionary
def test_word_han_viet_association_duplicate_binding_raises_integrity_error(session: Session, make_word, make_root,
                                                                            bind_word_han_viet):
    """Verifies that inserting a duplicate word-to-root mapping violates composite primary key constraints."""
    word = make_word(viet_word="pháp luật", english_translation="law")
    root = make_root(root="pháp", chinese_character="法", root_meaning="law")

    # Bind the pair once
    bind_word_han_viet(word.id, root.id)

    with pytest.raises(IntegrityError):
        # Attempting to bind the exact same composite pair a second time must fail
        session.execute(
            word_han_viet_association.insert().values(
                word_id=word.id,
                root_id=root.id
            )
        )
        session.commit()
