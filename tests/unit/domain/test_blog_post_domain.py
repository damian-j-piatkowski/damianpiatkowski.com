"""Unit tests for the BlogPost domain model.

These tests verify the correct initialization and attribute handling of
BlogPost instances, ensuring that required fields are properly assigned.

Tests included:
    - test_blog_post_creation: Ensures a BlogPost instance is created with expected attributes.
    - test_blog_post_created_at: Ensures the created_at timestamp is correctly set.
    - test_blog_post_drive_file_id: Ensures the drive_file_id is assigned correctly.
    - test_blog_post_slug: Ensures the slug is assigned correctly.
    - test_blog_post_title_and_content: Ensures title and content attributes are properly set.
"""

from datetime import datetime, timezone

from freezegun import freeze_time

from app.domain.blog_post import BlogPost


def test_blog_post_creation():
    """Ensures a BlogPost instance is created with expected attributes."""
    post = BlogPost(
        title="Test Title",
        content="Test Content",
        drive_file_id="drive123",
        slug="test-title"
    )

    assert post.title == "Test Title"
    assert post.content == "Test Content"
    assert post.drive_file_id == "drive123"
    assert post.slug == "test-title"
    assert isinstance(post.created_at, datetime)


@freeze_time("2025-03-17T12:00:00Z")
def test_blog_post_created_at():
    """Ensures the created_at timestamp is correctly set."""
    expected_timestamp = datetime(2025, 3, 17, 12, 0, 0, tzinfo=timezone.utc)
    post = BlogPost(
        title="Test Title",
        content="Test Content",
        drive_file_id="drive123",
        slug="test-title"
    )

    assert post.created_at == expected_timestamp


def test_blog_post_drive_file_id():
    """Ensures the drive_file_id is assigned correctly."""
    post = BlogPost(
        title="Test Title",
        content="Test Content",
        drive_file_id="drive-file-456",
        slug="test-title"
    )

    assert post.drive_file_id == "drive-file-456"


def test_blog_post_slug():
    """Ensures the slug is assigned correctly."""
    post = BlogPost(
        title="Test Title",
        content="Test Content",
        drive_file_id="drive123",
        slug="test-title"
    )

    assert post.slug == "test-title"


def test_blog_post_title_and_content():
    """Ensures title and content attributes are properly set."""
    post = BlogPost(
        title="Example Post",
        content="Example Content",
        drive_file_id="drive-file-789",
        slug="example-post"
    )

    assert post.title == "Example Post"
    assert post.content == "Example Content"
