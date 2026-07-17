"""Integration tests for the dictionary_examples table schema and constraints.

This module evaluates cascading delete actions, foreign key integrity rules, and index
traversal properties for contextual example sentences.
"""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.tables.dictionary_example import dictionary_examples
from app.models.tables.dictionary_source import dictionary_sources
from app.models.tables.dictionary_word import dictionary_words


@pytest.mark.dictionary
def test_dictionary_example_creation_and_hydration(session: Session, make_word, make_source, make_example):
    """Verifies that a dictionary example can be successfully inserted and read back with audit timestamps."""
    word = make_word(viet_word="chúc mừng", english_translation="to congratulate")
    source = make_source(source_type="colloquial", title="Daily Chat", url=None)

    example = make_example(
        word_id=word.id,
        source_id=source.id,
        sentence="Chúc mừng sinh nhật!",
        english_translation="Happy birthday!"
    )

    row = session.execute(
        dictionary_examples.select().where(dictionary_examples.c.id == example.id)
    ).fetchone()

    assert row is not None
    assert row.sentence == "Chúc mừng sinh nhật!"
    assert row.created_at is not None
    assert row.updated_at is not None


@pytest.mark.dictionary
def test_dictionary_example_cascade_on_word_deletion(session: Session, seed_dictionary):
    """Verifies that deleting a dictionary word automatically purges its dependent examples while leaving sources intact."""
    data = seed_dictionary()
    word_to_delete = data["words"][0]  # "học tập"
    associated_example_id = data["examples"][0].id
    associated_source_id = data["sources"][1].id  # "Từ Điển Tiếng Việt"

    # Delete the word
    session.execute(
        dictionary_words.delete().where(dictionary_words.c.id == word_to_delete.id)
    )
    session.commit()

    # Verify the child example is swept away
    example_exists = session.execute(
        dictionary_examples.select().where(dictionary_examples.c.id == associated_example_id)
    ).fetchone()
    assert example_exists is None

    # Verify the independent parent source is preserved
    source_exists = session.execute(
        dictionary_sources.select().where(dictionary_sources.c.id == associated_source_id)
    ).fetchone()
    assert source_exists is not None


@pytest.mark.dictionary
def test_dictionary_example_cascade_on_source_deletion(session: Session, seed_dictionary):
    """Verifies that deleting a citation source automatically purges its dependent examples while leaving words intact."""
    data = seed_dictionary()
    source_to_delete = data["sources"][0]  # "Truyện Kiều"
    associated_example_id = data["examples"][1].id
    associated_word_id = data["words"][1].id  # "nhân viên"

    # Delete the source
    session.execute(
        dictionary_sources.delete().where(dictionary_sources.c.id == source_to_delete.id)
    )
    session.commit()

    # Verify the child example is swept away
    example_exists = session.execute(
        dictionary_examples.select().where(dictionary_examples.c.id == associated_example_id)
    ).fetchone()
    assert example_exists is None

    # Verify the independent parent word is preserved
    word_exists = session.execute(
        dictionary_words.select().where(dictionary_words.c.id == associated_word_id)
    ).fetchone()
    assert word_exists is not None


@pytest.mark.dictionary
def test_dictionary_example_null_foreign_keys_raise_integrity_error(session: Session, make_word):
    """Verifies that inserting a dictionary example without linking it to a parent word or source raises an IntegrityError."""
    word = make_word()

    with pytest.raises(IntegrityError):
        session.execute(
            dictionary_examples.insert().values(
                word_id=word.id,
                source_id=None,  # Violates NOT NULL constraint
                sentence="Sentence without a source.",
                english_translation="Error expected."
            )
        )
        session.commit()
