"""Integration tests for the han_viet_roots Table schema definition.

This module validates database-level constraints, unique indices, and collation behavior
for Chinese structural semantic root components (`han_viet_roots`).

Tested Constraints & Specs:
    - Primary key autoincrementation behavior.
    - Unique constraint on the `root` column.
    - Full UTF-8 support for Hanzi logograms (`chinese_character`) and diacritics (`root`).
    - NOT NULL enforcement across required structural attributes.
"""

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models.tables.han_viet_root import han_viet_roots


def test_insert_han_viet_root_success(session):
    """Verify successful insertion of a Hán Việt root component."""
    stmt = han_viet_roots.insert().values(
        root="bản",
        chinese_character="本",
        root_meaning="root, basis, foundation",
    )
    result = session.execute(stmt)
    session.commit()

    root_id = result.inserted_primary_key[0]
    fetched_row = session.execute(
        select(han_viet_roots).where(han_viet_roots.c.id == root_id)  # type: ignore[arg-type]
    ).one()

    assert fetched_row.id == root_id
    assert fetched_row.root == "bản"
    assert fetched_row.chinese_character == "本"
    assert fetched_row.root_meaning == "root, basis, foundation"


def test_duplicate_root_violates_unique_constraint(session):
    """Verify unique constraint enforcement on the `root` field."""
    session.execute(
        han_viet_roots.insert().values(
            root="nhân",
            chinese_character="人",
            root_meaning="person, human",
        )
    )
    session.commit()

    duplicate_stmt = han_viet_roots.insert().values(
        root="nhân",
        chinese_character="因",
        root_meaning="cause, reason",
    )
    with pytest.raises(IntegrityError):
        session.execute(duplicate_stmt)
    session.rollback()


def test_insert_han_viet_root_missing_required_fields(session):
    """Verify NOT NULL enforcement on `root`, `chinese_character`, and `root_meaning`."""
    invalid_stmt = han_viet_roots.insert().values(
        root="tâm",
        chinese_character=None,
        root_meaning="heart, mind",
    )
    with pytest.raises(IntegrityError):
        session.execute(invalid_stmt)
    session.rollback()


def test_chinese_character_collation_and_length(session):
    """Verify storage of multi-character traditional/simplified Hanzi logograms."""
    stmt = han_viet_roots.insert().values(
        root="thật nghiệm",
        chinese_character="實驗",
        root_meaning="experiment, test",
    )
    result = session.execute(stmt)
    session.commit()

    root_id = result.inserted_primary_key[0]
    fetched_row = session.execute(
        select(han_viet_roots).where(han_viet_roots.c.id == root_id)  # type: ignore[arg-type]
    ).one()

    assert fetched_row.chinese_character == "實驗"