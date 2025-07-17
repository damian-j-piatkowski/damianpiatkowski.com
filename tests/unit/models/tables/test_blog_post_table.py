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

from datetime import datetime, timezone

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import column, select

from app.models.tables.blog_post import blog_posts


def test_drive_file_id_uniqueness_constraint(session):
    """Ensures duplicate Google Drive file IDs are not allowed."""
    session.execute(blog_posts.insert().values(
        title="Post A",
        slug="post-a",
        html_content="<p>First post content.</p>",
        drive_file_id="drive-unique-123",
    ))
    session.commit()

    with pytest.raises(IntegrityError):
        session.execute(blog_posts.insert().values(
            title="Post B",
            slug="post-b",
            html_content="<p>Second post content.</p>",
            drive_file_id="drive-unique-123",
        ))
        session.commit()


def test_insert_blog_post(session):
    """Verifies a blog post can be inserted and retrieved correctly from MySQL."""
    insert_stmt = blog_posts.insert().values(
        title="Test Post",
        slug="test-post",
        html_content="<p>This is a test post.</p>",
        drive_file_id="drive-file-123",
        created_at=datetime(2024, 3, 17, 12, 0, 0, tzinfo=timezone.utc),
    )
    session.execute(insert_stmt)
    session.commit()

    query_stmt = select(blog_posts).where(column("slug") == "test-post")
    result = session.execute(query_stmt).fetchone()

    assert result is not None
    assert result.title == "Test Post"
    assert result.slug == "test-post"
    assert result.html_content == "<p>This is a test post.</p>"
    assert result.drive_file_id == "drive-file-123"

    # Handle MySQL returning a naive datetime
    result_timestamp = result.created_at.replace(tzinfo=timezone.utc)
    expected_timestamp = datetime(2024, 3, 17, 12, 0, 0, tzinfo=timezone.utc)
    assert result_timestamp == expected_timestamp


def test_slug_uniqueness_constraint(session):
    """Ensures duplicate slugs are not allowed."""
    session.execute(blog_posts.insert().values(
        title="Post One",
        slug="unique-slug",
        html_content="<p>Content of post one.</p>",
        drive_file_id="drive-file-1",
    ))
    session.commit()

    with pytest.raises(IntegrityError):
        session.execute(blog_posts.insert().values(
            title="Post Two",
            slug="unique-slug",
            html_content="<p>Content of post two.</p>",
            drive_file_id="drive-file-2",
        ))
        session.commit()


def test_title_uniqueness_constraint(session):
    """Ensures duplicate titles are not allowed."""
    session.execute(blog_posts.insert().values(
        title="Non-Duplicate Title",
        slug="slug-1",
        html_content="<p>Content of post one.</p>",
        drive_file_id="drive-file-1",
    ))
    session.commit()

    with pytest.raises(IntegrityError):
        session.execute(blog_posts.insert().values(
            title="Non-Duplicate Title",
            slug="slug-2",
            html_content="<p>Content of post two.</p>",
            drive_file_id="drive-file-2",
        ))
        session.commit()
