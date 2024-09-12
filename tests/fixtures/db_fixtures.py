"""Database-related pytest fixtures.

This module includes fixtures for initializing the database, managing database
sessions during tests, and creating sample data objects like blog posts and log
entries for testing purposes.

Fixtures:
    - create_blog_post: Creates and commits a BlogPost instance for testing.
    - create_log: Creates and commits a Log instance for testing.
    - _db: Provides a session-wide test database with created tables.
    - session: Creates a new database session for each test function.
"""
from typing import Callable, Generator

import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Session, sessionmaker

from app import db
from app.domain.blog_post import BlogPost
from app.domain.log import Log
from app.models.blog_post import metadata as blog_post_metadata
from app.models.log import metadata as log_metadata

# List of metadata objects to manage database tables
all_metadata = [blog_post_metadata, log_metadata]


@pytest.fixture(scope='function')
def create_blog_post(session: Session) -> Callable[..., BlogPost]:
    """Fixture to create a BlogPost instance (commit happens in the test)."""

    def _create_blog_post(
        title='Test Post',
        content='This is a test post content',
        image_small='path/to/small/image.jpg',
        image_medium='path/to/medium/image.jpg',
        image_large='path/to/large/image.jpg',
        url='test-post'
    ) -> BlogPost:
        post = BlogPost(
            title=title,
            content=content,
            image_small=image_small,
            image_medium=image_medium,
            image_large=image_large,
            url=url
        )
        session.add(post)
        return post  # Commit responsibility is moved to the test

    return _create_blog_post



@pytest.fixture(scope='function')
def create_log(session: Session) -> Callable[..., Log]:
    """Fixture to create a Log instance (commit happens in the test)."""

    def _create_log(
        level='INFO',
        message='Test log message'
    ) -> Log:
        log_entry = Log(
            level=level,
            message=message
        )
        session.add(log_entry)
        return log_entry  # Commit responsibility is moved to the test

    return _create_log



@pytest.fixture(scope='function')
def _db(app: Flask) -> Generator[SQLAlchemy, None, None]:
    """
    Provides a session-wide test database with created tables.
    """
    with app.app_context():
        # Create all tables from metadata
        for metadata in all_metadata:
            metadata.create_all(bind=db.engine)
        yield db
        # Drop all tables after tests are done
        for metadata in all_metadata:
            metadata.drop_all(bind=db.engine)


@pytest.fixture(scope='function')
def session(_db: SQLAlchemy) -> Generator[Session, None, None]:
    """
    Creates a new database session for each test function.
    """
    # Establish a connection and begin a transaction
    connection = _db.engine.connect()
    transaction = connection.begin()

    # Create a session factory bound to the current connection (no scoped sess.)
    session_factory = sessionmaker(bind=connection)
    test_session = session_factory()

    try:
        # Provide the session to the test
        yield test_session
    except Exception as e:
        print(f"Error during test session: {e}")
        raise
    finally:
        # Ensure rollback and cleanup are executed regardless of test outcome
        if transaction.is_active:
            transaction.rollback()
        connection.close()
        test_session.close()
