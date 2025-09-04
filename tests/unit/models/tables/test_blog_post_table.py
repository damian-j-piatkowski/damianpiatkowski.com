"""Integration tests for the blog_posts table.

This module verifies the integration of the blog_posts table with the database.
It ensures that blog posts can be inserted, queried, and that constraints such
as uniqueness and required fields are enforced.

Test cases:
    - test_drive_file_id_uniqueness_constraint: Ensures duplicate drive_file_ids are not allowed.
    - test_insert_blog_post: Verifies a blog post is correctly inserted and retrievable.
    - test_slug_uniqueness_constraint: Ensures duplicate slugs are not allowed.
    - test_title_uniqueness_constraint: Ensures duplicate titles are not allowed.
"""

from datetime import datetime

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import column, select

from app.models.tables.blog_post import blog_posts


def _base_post_values(**overrides):
    """Helper to provide all required blog_post fields with sensible defaults."""
    base = dict(
        title="Default Title",
        slug="default-slug",
        html_content="<p>Default content.</p>",
        drive_file_id="default-drive-id",
        meta_description="Default meta description",
        keywords=["default", "keyword"],
        read_time_minutes=3,
        categories=["default", "category"],
    )
    base.update(overrides)
    return base


def test_drive_file_id_uniqueness_constraint(session):
    """Ensures duplicate Google Drive file IDs are not allowed."""
    session.execute(blog_posts.insert().values(
        **_base_post_values(title="Post A", slug="post-a", drive_file_id="drive-unique-123")
    ))
    session.commit()

    with pytest.raises(IntegrityError):
        session.execute(blog_posts.insert().values(
            **_base_post_values(title="Post B", slug="post-b", drive_file_id="drive-unique-123")
        ))
        session.commit()


def test_insert_blog_post(session):
    """Verifies a blog post can be inserted and retrieved correctly from MySQL."""
    session.execute(blog_posts.insert().values(
        **_base_post_values(
            title="Test Post",
            slug="test-post",
            html_content="<p>This is a test post.</p>",
            drive_file_id="drive-file-123",
        )
    ))
    session.commit()

    query_stmt = select(blog_posts).where(column("slug") == "test-post")
    result = session.execute(query_stmt).fetchone()

    assert result is not None
    assert result.title == "Test Post"
    assert result.slug == "test-post"
    assert result.html_content == "<p>This is a test post.</p>"
    assert result.drive_file_id == "drive-file-123"
    assert isinstance(result.created_at, datetime)
    assert isinstance(result.updated_at, datetime)


def test_slug_uniqueness_constraint(session):
    """Ensures duplicate slugs are not allowed."""
    session.execute(blog_posts.insert().values(
        **_base_post_values(title="Post One", slug="unique-slug", drive_file_id="drive-file-1")
    ))
    session.commit()

    with pytest.raises(IntegrityError):
        session.execute(blog_posts.insert().values(
            **_base_post_values(title="Post Two", slug="unique-slug", drive_file_id="drive-file-2")
        ))
        session.commit()


def test_title_uniqueness_constraint(session):
    """Ensures duplicate titles are not allowed."""
    session.execute(blog_posts.insert().values(
        **_base_post_values(title="Non-Duplicate Title", slug="slug-1", drive_file_id="drive-file-1")
    ))
    session.commit()

    with pytest.raises(IntegrityError):
        session.execute(blog_posts.insert().values(
            **_base_post_values(title="Non-Duplicate Title", slug="slug-2", drive_file_id="drive-file-2")
        ))
        session.commit()
