"""Unit tests for the BlogPost domain model.

These tests verify the correct initialization and attribute handling of
BlogPost instances, ensuring that required fields are properly assigned.

Tests included:
    - test_blog_post_creation: Ensures a BlogPost instance is created with expected attributes.
    - test_blog_post_drive_file_id: Ensures the drive_file_id is assigned correctly.
    - test_blog_post_slug: Ensures the slug is assigned correctly.
    - test_blog_post_title_and_content: Ensures title and content attributes are properly set.
"""

from datetime import datetime, timezone

import pytest

from app.domain.blog_post import BlogPost


@pytest.mark.admin_upload_blog_posts
@pytest.mark.render_blog_posts
@pytest.mark.render_single_blog_post
def test_blog_post_creation():
    """Ensures a BlogPost instance is created with expected attributes."""
    created_at = datetime(2025, 3, 17, 12, 0, 0, tzinfo=timezone.utc)

    post = BlogPost(
        title="Test Title",
        content="Test Content",
        drive_file_id="drive123",
        slug="test-title",
        created_at=created_at
    )

    assert post.title == "Test Title"
    assert post.content == "Test Content"
    assert post.drive_file_id == "drive123"
    assert post.slug == "test-title"
    assert post.created_at == created_at
    assert isinstance(post.created_at, datetime)
    assert post.created_at.tzinfo == timezone.utc  # Ensure UTC timezone


@pytest.mark.admin_upload_blog_posts
@pytest.mark.render_blog_posts
@pytest.mark.render_single_blog_post
def test_blog_post_drive_file_id():
    """Ensures the drive_file_id is assigned correctly."""
    created_at = datetime(2025, 3, 17, 12, 0, 0, tzinfo=timezone.utc)

    post = BlogPost(
        title="Test Title",
        content="Test Content",
        drive_file_id="drive-file-456",
        slug="test-title",
        created_at=created_at
    )

    assert post.drive_file_id == "drive-file-456"
    assert isinstance(post.created_at, datetime)
    assert post.created_at.tzinfo == timezone.utc  # Ensure UTC timezone


@pytest.mark.admin_upload_blog_posts
@pytest.mark.render_blog_posts
@pytest.mark.render_single_blog_post
def test_blog_post_slug():
    """Ensures the slug is assigned correctly."""
    created_at = datetime(2025, 3, 17, 12, 0, 0, tzinfo=timezone.utc)

    post = BlogPost(
        title="Test Title",
        content="Test Content",
        drive_file_id="drive123",
        slug="test-title",
        created_at=created_at
    )

    assert post.slug == "test-title"
    assert isinstance(post.created_at, datetime)
    assert post.created_at.tzinfo == timezone.utc  # Ensure UTC timezone


@pytest.mark.admin_upload_blog_posts
@pytest.mark.render_blog_posts
@pytest.mark.render_single_blog_post
def test_blog_post_title_and_content():
    """Ensures title and content attributes are properly set."""
    created_at = datetime(2025, 3, 17, 12, 0, 0, tzinfo=timezone.utc)

    post = BlogPost(
        title="Example Post",
        content="Example Content",
        drive_file_id="drive-file-789",
        slug="example-post",
        created_at=created_at
    )

    assert post.title == "Example Post"
    assert post.content == "Example Content"
    assert isinstance(post.created_at, datetime)
    assert post.created_at.tzinfo == timezone.utc  # Ensure UTC timezone
