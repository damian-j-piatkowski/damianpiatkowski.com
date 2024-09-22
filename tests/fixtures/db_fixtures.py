"""Database-related pytest fixtures.

This module includes fixtures for initializing the database and managing
database sessions during tests.

Fixtures:
    - _db: Provides a session-wide test database with created tables.
    - session: Creates a new database session for each test function.
"""
from typing import Generator

import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Session, sessionmaker

from app import db
from app.models.blog_post import metadata as blog_post_metadata
from app.models.log import metadata as log_metadata

# List of metadata objects to manage database tables
all_metadata = [blog_post_metadata, log_metadata]


@pytest.fixture(scope='function')
def _db(app: Flask) -> Generator[SQLAlchemy, None, None]:
    """
    Provides a session-wide test database with created tables.
    """
    with app.app_context():
        for metadata in all_metadata:
            metadata.create_all(bind=db.engine)
        yield db
        for metadata in all_metadata:
            metadata.drop_all(bind=db.engine)


@pytest.fixture(scope='function')
def session(_db: SQLAlchemy) -> Generator[Session, None, None]:
    """
    Creates a new database session for each test function.
    """
    connection = _db.engine.connect()
    transaction = connection.begin()

    session_factory = sessionmaker(bind=connection)
    test_session = session_factory()

    try:
        yield test_session
    except Exception as e:
        print(f"Error during test session: {e}")
        raise
    finally:
        if transaction.is_active:
            transaction.rollback()
        connection.close()
        test_session.close()
