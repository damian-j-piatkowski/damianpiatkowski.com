# tests/fixtures/db_fixtures.py

"""Database-related pytest fixtures.

This module includes fixtures for initializing the database and managing
database sessions during tests. These fixtures ensure that each test runs in
a clean database environment, preventing data persistence across tests.
"""

import os
from typing import Generator

import pytest
from flask import Flask
from flask_migrate import upgrade
from flask_sqlalchemy import SQLAlchemy
# 👇 Import reflect to grab whatever happens to live in the test DB
from sqlalchemy import MetaData
from sqlalchemy.orm import Session, sessionmaker

from app import db


def prepare_integration_db(app: Flask) -> None:
    """Programmatically cleans and updates the test database schema using migrations.

    Bypasses step-by-step downgrades to avoid FileNotFoundError and Missing Table errors.
    """
    with app.app_context():
        os.environ['FLASK_ENV'] = 'testing'
        migrations_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'migrations')

        print("\n[Test DB Setup] Purging any lingering tables...")
        # Reflect whatever is physically in the DB right now and drop it clean
        raw_metadata = MetaData()
        raw_metadata.reflect(bind=db.engine)
        raw_metadata.drop_all(bind=db.engine)

        print("[Alembic via Flask-Migrate] Applying fresh migration changes to head...")
        upgrade(directory=migrations_dir, revision='head')


@pytest.fixture(scope='session')
def _db(app: Flask) -> Generator[SQLAlchemy, None, None]:
    """Sets up the schema via migrations ONCE per test session."""
    prepare_integration_db(app)

    with app.app_context():
        yield db


@pytest.fixture(scope='function')
def session(_db: SQLAlchemy) -> Generator[Session, None, None]:
    """Provides a fresh database session for each test function."""
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
        test_session.close()
        if transaction.is_active:
            transaction.rollback()
        connection.close()
