"""Integration tests for the create_blog_post repository method.

This module contains integration tests for the create_blog_post method of
the BlogPostRepository class, verifying its behavior in inserting new
blog posts into the database.

Tests included:
    - test_create_blog_post_created_at: Ensures the created_at timestamp is correctly assigned.
    - test_create_blog_post_duplicate_drive_file_id: Ensures an error is raised when inserting a duplicate drive_file_id.
    - test_create_blog_post_duplicate_slug: Ensures an error is raised when inserting a duplicate slug.
    - test_create_blog_post_failure: Ensures a RuntimeError is raised when a database error occurs.
    - test_create_blog_post_long_content: Handles very long content fields.
    - test_create_blog_post_missing_content: Ensures an IntegrityError is raised when content is missing.
    - test_create_blog_post_special_characters: Handles titles and content with special characters.
    - test_create_blog_post_valid: Ensures successful insertion of a new post.

Fixtures:
    - session: Provides a database session.
"""

from datetime import datetime, timezone, timedelta

import pytest
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.exceptions import BlogPostDuplicateError
from app.models.repositories.blog_post_repository import BlogPostRepository


@pytest.mark.admin_upload_blog_posts
def test_create_blog_post_created_at(session):
    """Ensures the created_at timestamp is correctly assigned."""
    repository = BlogPostRepository(session)
    post = repository.create_blog_post(
        title="Timestamp Test",
        slug="timestamp-test",
        content="Checking created_at field",
        drive_file_id="drive-timestamp"
    )

    assert post.created_at is not None
    assert isinstance(post.created_at, datetime)

    # Make post.created_at timezone-aware
    post_created_at = post.created_at.replace(tzinfo=timezone.utc)

    assert post_created_at <= datetime.now(timezone.utc) + timedelta(seconds=1)


@pytest.mark.admin_upload_blog_posts
def test_create_blog_post_duplicate_drive_file_id(session):
    """Ensures an error is raised when inserting a blog post with a duplicate drive_file_id."""
    repository = BlogPostRepository(session)

    # Arrange - Create initial post
    repository.create_blog_post(title="First Post", slug="first-post", content="Some content", drive_file_id="drive123")

    # Act & Assert - Attempt to create another post with the same drive_file_id
    with pytest.raises(BlogPostDuplicateError, match="A blog post with this drive_file_id already exists."):
        repository.create_blog_post(title="Another Post", slug="another-post", content="Different content",
                                    drive_file_id="drive123")


@pytest.mark.admin_upload_blog_posts
def test_create_blog_post_duplicate_slug(session):
    """Ensures an error is raised when inserting a blog post with a duplicate slug."""
    repository = BlogPostRepository(session)

    # Arrange - Create initial post
    repository.create_blog_post(title="First Post", slug="duplicate-slug", content="Some content",
                                drive_file_id="drive123")

    # Act & Assert - Attempt to create another post with the same slug
    with pytest.raises(BlogPostDuplicateError, match="A blog post with this slug already exists."):
        repository.create_blog_post(title="Another Post", slug="duplicate-slug", content="Different content",
                                    drive_file_id="drive456")


@pytest.mark.admin_upload_blog_posts
def test_create_blog_post_failure(session, monkeypatch):
    """Ensures a RuntimeError is raised when a database error occurs."""
    repository = BlogPostRepository(session)

    # Simulate a SQLAlchemyError
    monkeypatch.setattr(session, 'execute', lambda *args, **kwargs: (_ for _ in ()).throw(SQLAlchemyError()))

    with pytest.raises(RuntimeError, match="Failed to create blog post in the database."):
        repository.create_blog_post(
            title='Fail Title',
            slug='fail-title',
            content='Fail Content',
            drive_file_id='fail-drive-file-id'
        )


@pytest.mark.admin_upload_blog_posts
def test_create_blog_post_long_content(session):
    """Handles very long content fields."""
    repository = BlogPostRepository(session)
    long_content = "A" * 5000  # 5000 characters

    post = repository.create_blog_post(title="Long Content Post", slug="long-content-post", content=long_content,
                                       drive_file_id="drive789")

    assert post.title == "Long Content Post"
    assert post.content == long_content
    assert post.slug == "long-content-post"
    assert post.drive_file_id == "drive789"


@pytest.mark.admin_upload_blog_posts
def test_create_blog_post_missing_content(session):
    """Ensures an IntegrityError is raised when attempting to insert a blog post without content."""
    repository = BlogPostRepository(session)

    # Act & Assert: Attempt to create a post with `None` content
    with pytest.raises(IntegrityError, match="NOT NULL constraint failed: blog_posts.content"):
        repository.create_blog_post(
            title='Missing Content Post',
            slug='missing-content',
            content=None,  # type: ignore
            drive_file_id='missing-content-file-id'
        )


@pytest.mark.admin_upload_blog_posts
def test_create_blog_post_special_characters(session):
    """Handles titles and content with special characters."""
    repository = BlogPostRepository(session)

    post = repository.create_blog_post(title="Spécîål 💡 Tîtle", slug="special-title",
                                       content="Côntênt with 🎉 emojis & symbols!", drive_file_id="drive987")

    assert post.title == "Spécîål 💡 Tîtle"
    assert post.content == "Côntênt with 🎉 emojis & symbols!"
    assert post.slug == "special-title"
    assert post.drive_file_id == "drive987"


@pytest.mark.admin_upload_blog_posts
def test_create_blog_post_valid(session):
    """Ensures a blog post is successfully created in the database."""
    repository = BlogPostRepository(session)

    post = repository.create_blog_post(title="Valid Post", slug="valid-post", content="Valid Content",
                                       drive_file_id="drive654")

    assert post.title == "Valid Post"
    assert post.content == "Valid Content"
    assert post.slug == "valid-post"
    assert post.drive_file_id == "drive654"
