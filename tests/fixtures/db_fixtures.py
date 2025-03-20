"""Database-related pytest fixtures.

This module includes fixtures for initializing the database and managing
database sessions during tests. These fixtures ensure that each test runs in
a clean database environment, preventing data persistence across tests.

Fixtures:
    - _db: Sets up a fresh test database with tables created before each test
           and dropped afterward to maintain test isolation.
    - session: Provides a new database session for each test function, using
               transactions to ensure that database state resets automatically.
"""
from typing import Generator

import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Session, sessionmaker

from app import db
from app.models.tables.blog_post import metadata as blog_post_metadata
from app.models.tables.log import metadata as log_metadata

# List of metadata objects to manage database tables
all_metadata = [blog_post_metadata, log_metadata]


@pytest.fixture(scope='function')
def _db(app: Flask) -> Generator[SQLAlchemy, None, None]:
    """Sets up a fresh test database before each test and tears it down afterward.

    This fixture:
    - Runs within the Flask application context to ensure proper access to `db`.
    - Creates all necessary tables at the start of each test.
    - Yields the database instance for use in tests.
    - Drops all tables after the test completes to clean up.

    This guarantees a clean slate for every test, preventing data contamination.
    """
    with app.app_context():
        for metadata in all_metadata:
            metadata.create_all(bind=db.engine)
        yield db
        for metadata in all_metadata:
            metadata.drop_all(bind=db.engine)


@pytest.fixture(scope='function')
def session(_db: SQLAlchemy) -> Generator[Session, None, None]:
    """Provides a fresh database session for each test function.

    This fixture:
    - Establishes a **new connection** to the test database.
    - Begins a **transaction**, ensuring all changes are rolled back after the test.
    - Uses a **session factory** to create an independent session for each test.
    - Yields the session to the test function.
    - Rolls back any changes made during the test to keep the database clean.
    - Closes the session and connection afterward.

    Since the transaction is rolled back at the end of each test, no data persists,
    ensuring each test starts with a **pristine database state**.
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
