"""Unit tests for the fetch_all_post_identifiers repository method.

This module contains unit tests for the fetch_all_post_identifiers method of
the BlogPostRepository class. It verifies that the method correctly retrieves only
the lightweight identifiers of blog posts from the database.

Tests included:
    - test_fetch_all_post_identifiers_empty_db: Ensures an empty list is returned when no blog posts exist.
    - test_fetch_all_post_identifiers_error_handling: Simulates a SQLAlchemy error to verify proper exception handling.
    - test_fetch_all_post_identifiers_matches_seeded_posts: Ensures the identifiers match the expected values based on seeded blog posts.
    - test_fetch_all_post_identifiers_returns_expected_structure: Verifies that the returned list contains dicts with slug, title, and drive_file_id.

Fixtures:
    - seed_blog_posts: Function fixture for seeding a specified number of blog posts.
    - session: Provides a database session.
"""
from datetime import datetime
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.models.repositories.blog_post_repository import BlogPostRepository


@pytest.mark.admin_published_posts
@pytest.mark.admin_unpublished_posts
def test_fetch_all_post_identifiers_empty_db(session):
    """Ensures an empty list is returned when no blog posts exist."""
    repository = BlogPostRepository(session)
    identifiers = repository.fetch_all_post_identifiers()
    assert identifiers == []


@pytest.mark.admin_published_posts
@pytest.mark.admin_unpublished_posts
def test_fetch_all_post_identifiers_error_handling():
    """Simulates a SQLAlchemy error to verify proper exception handling."""
    broken_session = MagicMock()
    broken_session.execute.side_effect = SQLAlchemyError("Simulated DB failure")

    repository = BlogPostRepository(broken_session)

    with pytest.raises(RuntimeError, match="Failed to fetch blog post identifiers from the database."):
        repository.fetch_all_post_identifiers()


@pytest.mark.admin_published_posts
@pytest.mark.admin_unpublished_posts
def test_fetch_all_post_identifiers_matches_seeded_posts(session, seed_blog_posts):
    """Ensures the identifiers match the expected values based on seeded blog posts."""
    seed_blog_posts(5)
    session.commit()
    repository = BlogPostRepository(session)

    identifiers = repository.fetch_all_post_identifiers()

    expected = [
        {
            "drive_file_id": f"drive_id_{i}",
            "slug": f"post-{i}",
            "title": f"Post {i}",
        }
        for i in range(1, 6)
    ]

    # Compare dicts without updated_at
    stripped_identifiers = [
        {k: v for k, v in identifier.items() if k != "updated_at"}
        for identifier in identifiers
    ]

    assert sorted(stripped_identifiers, key=lambda x: x["slug"]) == sorted(expected, key=lambda x: x["slug"])

    # Just check that updated_at is a datetime
    for identifier in identifiers:
        assert isinstance(identifier["updated_at"], datetime)


@pytest.mark.admin_published_posts
@pytest.mark.admin_unpublished_posts
def test_fetch_all_post_identifiers_returns_expected_structure(session, seed_blog_posts):
    """Verifies that the returned list contains dicts with slug, title, drive_file_id, and updated_at."""
    seed_blog_posts(3)
    session.commit()
    repository = BlogPostRepository(session)

    identifiers = repository.fetch_all_post_identifiers()

    assert isinstance(identifiers, list)
    assert all(isinstance(item, dict) for item in identifiers)
    assert all(set(item.keys()) == {"slug", "title", "drive_file_id", "updated_at"} for item in identifiers)

    for item in identifiers:
        assert isinstance(item["slug"], str)
        assert isinstance(item["title"], str)
        assert isinstance(item["drive_file_id"], str)
        assert isinstance(item["updated_at"], datetime)
