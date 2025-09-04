"""Unit tests for the BlogPost domain model.

These tests verify the correct initialization and attribute handling of
BlogPost instances, ensuring that required fields are properly assigned.

Scenarios included:
    - Ensure a BlogPost instance is created with expected attributes.
    - Ensure the drive_file_id is assigned correctly.
    - Ensure the slug is assigned correctly.
    - Ensure title and content attributes are properly set.
"""

from datetime import datetime, timezone

import pytest

from app.domain.blog_post import BlogPost


@pytest.mark.admin_upload_blog_posts
@pytest.mark.render_blog_posts
@pytest.mark.render_single_blog_post
@pytest.mark.parametrize(
    "field, expected",
    [
        ("title", "Test Title"),
        ("html_content", "<p>Some test content</p>"),
        ("drive_file_id", "drive123"),
        ("slug", "test-title"),
    ],
)
def test_blog_post_fields(field, expected):
    """Ensures BlogPost fields are correctly assigned."""
    created_at = datetime(2025, 3, 17, 12, 0, 0, tzinfo=timezone.utc)

    post = BlogPost(
        title="Test Title",
        html_content="<p>Some test content</p>",
        drive_file_id="drive123",
        slug="test-title",
        created_at=created_at,
        updated_at=created_at,
        read_time_minutes=2,
        meta_description="Test meta description",
        keywords=['test', 'keyword'],
        categories=["test", "category", "list"],
    )

    assert getattr(post, field) == expected
    assert isinstance(post.created_at, datetime)
    assert post.created_at.tzinfo == timezone.utc  # Ensure UTC timezone
