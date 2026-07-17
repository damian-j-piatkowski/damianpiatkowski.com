"""Integration tests for the dictionary_words table schema and constraints.

This module evaluates unique validation constraints, case-sensitive collisions, and
prefix-based index lookup operations on the central word repository.
"""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.tables.dictionary_word import dictionary_words


@pytest.mark.dictionary
def test_dictionary_word_creation_and_uniqueness(session: Session, make_word):
    """Verifies that dictionary words are successfully persisted and reject duplicates on unique column constraints."""
    make_word(viet_word="sách", english_translation="book")

    with pytest.raises(IntegrityError):
        # Attempting to insert a duplicate 'viet_word' must fail
        session.execute(
            dictionary_words.insert().values(
                viet_word="sách",
                english_translation="another book description"
            )
        )
        session.commit()


@pytest.mark.dictionary
def test_dictionary_word_collation_is_case_insensitive_on_unique_constraint(session: Session, make_word):
    """Verifies that unique constraints are validated case-insensitively due to the configured collation."""
    make_word(viet_word="cà phê", english_translation="coffee")

    with pytest.raises(IntegrityError):
        # collation utf8mb4_unicode_ci is case-insensitive, meaning "Cà Phê" collides with "cà phê"
        session.execute(
            dictionary_words.insert().values(
                viet_word="Cà Phê",
                english_translation="Coffee (Uppercase)"
            )
        )
        session.commit()


@pytest.mark.dictionary
def test_dictionary_word_prefix_index_lookup(session: Session, make_word):
    """Verifies that words can be matched and queried by prefix, validating the performance lookup indices."""
    make_word(viet_word="bàn học", english_translation="study desk")
    make_word(viet_word="bàn ăn", english_translation="dining table")
    make_word(viet_word="ghế", english_translation="chair")

    # Match prefix 'bàn' using a standard wildcard query
    query = dictionary_words.select().where(dictionary_words.c.viet_word.like("bàn%"))
    results = session.execute(query).fetchall()

    assert len(results) == 2
    words = {row.viet_word for row in results}
    assert "bàn học" in words
    assert "bàn ăn" in words
