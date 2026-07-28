"""Integration tests for the word_type_association Table schema definition.

This module validates the composite primary key many-to-many junction bridge table
connecting vocabulary words (`dictionary_words`) with grammatical classifications.

Tested Constraints & Specs:
    - Composite primary key uniqueness `(word_id, word_type)`.
    - Multiple type assignments for a single vocabulary word.
    - Database-level `ON DELETE CASCADE` when the referenced parent word is removed.
    - Foreign key failure when linking to a non-existent `word_id`.
"""

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models.tables.dictionary_word import dictionary_words
from app.models.tables.word_type_association import word_type_association


def test_assign_multiple_word_types_to_single_word(session, make_word):
    """Verifies mapping multiple grammatical types (noun + verb) to one dictionary word."""
    word = make_word(viet_word="báo cáo", english_translation="report, to report")

    session.execute(
        word_type_association.insert(),
        [
            {"word_id": word.id, "word_type": "noun"},
            {"word_id": word.id, "word_type": "verb"},
        ],
    )
    session.commit()

    rows = session.execute(
        select(word_type_association.c.word_type)
        .where(word_type_association.c.word_id == word.id)  # type: ignore[arg-type]
        .order_by(word_type_association.c.word_type)
    ).scalars().all()

    assert rows == ["noun", "verb"]


def test_duplicate_composite_primary_key_fails(session, make_word):
    """Verifies duplicate assignment of the same `(word_id, word_type)` pair raises IntegrityError."""
    word = make_word(viet_word="ăn", english_translation="to eat")

    session.execute(
        word_type_association.insert().values(word_id=word.id, word_type="verb")
    )
    session.commit()

    duplicate_stmt = word_type_association.insert().values(word_id=word.id, word_type="verb")
    with pytest.raises(IntegrityError):
        session.execute(duplicate_stmt)


def test_insert_non_existent_word_id_violates_foreign_key(session):
    """Verifies foreign key constraint failure when `word_id` references a non-existent row."""
    stmt = word_type_association.insert().values(word_id=99999, word_type="noun")
    with pytest.raises(IntegrityError):
        session.execute(stmt)


def test_deleting_dictionary_word_cascades_to_type_associations(session, make_word):
    """Verifies `ON DELETE CASCADE` cleans up junction rows when parent `dictionary_words` entry is deleted."""
    word = make_word(viet_word="chạy", english_translation="to run")

    session.execute(
        word_type_association.insert(),
        [
            {"word_id": word.id, "word_type": "verb"},
            {"word_id": word.id, "word_type": "noun"},
        ],
    )
    session.commit()

    # Direct Core DELETE on the parent dictionary word
    session.execute(
        dictionary_words.delete().where(dictionary_words.c.id == word.id)
    )
    session.commit()

    # Assert downstream bridge rows were swept clean by MySQL
    remaining_associations = session.execute(
        select(word_type_association).where(word_type_association.c.word_id == word.id)  # type: ignore[arg-type]
    ).fetchall()

    assert len(remaining_associations) == 0
