"""Integration tests for the users table schema definition.

This module validates relational database constraints, unique administrative handles,
and storage behavior for system user credentials.
"""

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.tables.user import users


def test_user_creation_and_hydration(session: Session):
    """Verifies that an administrative user record can be inserted and retrieved correctly."""
    stmt = users.insert().values(
        username="admin_damian",
        password_hash="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Bw59G"
    )
    result = session.execute(stmt)
    session.commit()

    inserted_id = result.inserted_primary_key[0]

    row = session.execute(
        select(users).where(users.c.id == inserted_id)
    ).fetchone()

    assert row is not None
    assert row.username == "admin_damian"
    assert row.password_hash == "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Bw59G"


def test_duplicate_username_raises_integrity_error(session: Session):
    """Verifies that inserting two user records with identical usernames violates unique constraints."""
    user_1 = {
        "username": "sysadmin",
        "password_hash": "hash_digest_1"
    }
    user_2 = {
        "username": "sysadmin",  # Duplicate username handle
        "password_hash": "hash_digest_2"
    }

    session.execute(users.insert().values(**user_1))
    session.commit()

    with pytest.raises(IntegrityError):
        session.execute(users.insert().values(**user_2))
        session.commit()


def test_null_username_or_password_hash_raises_integrity_error(session: Session):
    """Verifies that inserting a user without mandatory credentials triggers an IntegrityError."""
    invalid_user = {
        "username": "incomplete_admin",
        "password_hash": None  # Violates NOT NULL constraint
    }

    with pytest.raises(IntegrityError):
        session.execute(users.insert().values(**invalid_user))
        session.commit()