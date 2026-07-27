"""Integration tests for the dictionary_sources Table schema definition.

This module validates database-level constraints, index behavior, and field defaults for
the `dictionary_sources` table using SQLAlchemy Core operations against a live MySQL instance.

Tested Constraints & Specs:
    - Default generation of `created_at` timestamp.
    - Nullability rules for optional `url` vs. required `title` and `source_type`.
    - Database error handling (SQLAlchemyError/DataError) for missing required fields and column overflow.
    - Index usability for filtering over `source_type`.
"""

from datetime import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, DataError, SQLAlchemyError

from app.models.tables.dictionary_source import dictionary_sources


def test_insert_dictionary_source_with_all_fields(session):
    """Verifies successful insertion of a digital media source with an explicit URL."""
    stmt = dictionary_sources.insert().values(
        source_type="article",
        title="VnExpress - Messi điều chỉnh thế nào để giúp Argentina thắng ngược Ai Cập?",
        url="https://vnexpress.net/messi-dieu-chinh-the-nao-de-giup-argentina-thang-nguoc-ai-cap-5094933.html",
    )
    result = session.execute(stmt)
    session.commit()

    source_id = result.inserted_primary_key[0]
    fetched_row = session.execute(
        select(dictionary_sources).where(dictionary_sources.c.id == source_id)  # type: ignore[arg-type]
    ).one()

    assert fetched_row.id == source_id
    assert fetched_row.source_type == "article"
    assert fetched_row.title == "VnExpress - Messi điều chỉnh thế nào để giúp Argentina thắng ngược Ai Cập?"
    assert fetched_row.url == "https://vnexpress.net/messi-dieu-chinh-the-nao-de-giup-argentina-thang-nguoc-ai-cap-5094933.html"
    assert isinstance(fetched_row.created_at, datetime)


def test_insert_dictionary_source_omitting_optional_url(session):
    """Verifies insertion of a physical media source where URL is omitted (defaults to NULL)."""
    stmt = dictionary_sources.insert().values(
        source_type="book",
        title="21 bài học cho thế kỷ 21",
    )
    result = session.execute(stmt)
    session.commit()

    source_id = result.inserted_primary_key[0]
    fetched_row = session.execute(
        select(dictionary_sources).where(dictionary_sources.c.id == source_id)  # type: ignore[arg-type]
    ).one()

    assert fetched_row.id == source_id
    assert fetched_row.source_type == "book"
    assert fetched_row.title == "21 bài học cho thế kỷ 21"
    assert fetched_row.url is None


def test_insert_source_missing_required_title_fails(session):
    """Verifies missing required `title` raises a SQLAlchemy DB execution error."""
    stmt = dictionary_sources.insert().values(
        source_type="book",
        url="https://example.com/missing-title",
    )
    with pytest.raises(SQLAlchemyError):
        session.execute(stmt)
    session.rollback()


def test_insert_source_missing_required_source_type_fails(session):
    """Verifies missing required `source_type` raises a SQLAlchemy DB execution error."""
    stmt = dictionary_sources.insert().values(
        title="Source without type",
    )
    with pytest.raises(SQLAlchemyError):
        session.execute(stmt)
    session.rollback()


def test_source_type_field_length_overflow(session):
    """Verifies data truncation/overflow error when exceeding VARCHAR(32) on `source_type`."""
    long_type = "a" * 33
    stmt = dictionary_sources.insert().values(
        source_type=long_type,
        title="Overflow Source Type Test",
    )
    with pytest.raises((DataError, IntegrityError)):  # type: ignore[arg-type]
        session.execute(stmt)
    session.rollback()


def test_source_type_lookup_index_query_execution(session):
    """Verifies index performance path for `idx_sources_type_lookup` filtering."""
    session.execute(
        dictionary_sources.insert(),
        [
            {"source_type": "podcast", "title": "Vietcetera - Have a Sip #1"},
            {"source_type": "podcast", "title": "Vietcetera - Have a Sip #2"},
            {"source_type": "news", "title": "Tuổi Trẻ Online"},
        ],
    )
    session.commit()

    query = select(dictionary_sources).where(dictionary_sources.c.source_type == "podcast")  # type: ignore[arg-type]
    rows = session.execute(query).fetchall()

    assert len(rows) == 2
    assert all(row.source_type == "podcast" for row in rows)
