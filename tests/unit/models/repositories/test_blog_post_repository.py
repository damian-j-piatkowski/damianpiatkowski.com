"""Unit tests for the BlogPostRepository class.

This module contains tests for the `BlogPostRepository` class, which manages CRUD
operations for blog posts in the database.

Tests included:
    - test_create_blog_post_duplicate_title_failure: Verifies that creating a blog post
      with a duplicate title raises a BlogPostDuplicateError.
    - test_create_blog_post_failure: Verifies behavior when a SQLAlchemy error occurs during
      blog post creation.
    - test_create_blog_post_missing_content: Verifies that creating a blog post with missing
      content raises an IntegrityError.
    - test_create_blog_post_with_excessively_long_content: Verifies that overly long blog
      post content raises a RuntimeError.
    - test_create_multiple_blog_posts: Verifies successful creation of multiple blog posts,
      including 1, 2, 5, and 10 posts.
    - test_fetch_blog_posts_empty_db: Verifies that fetching all blog posts returns an empty
      list when the database is empty.

Fixtures:
    - session: Provides a database session for testing.
    - create_blog_post: Fixture to create blog posts in the database.
"""

import pytest
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.exceptions import BlogPostDuplicateError
from app.models.repositories.blog_post_repository import BlogPostRepository


def test_create_blog_post_duplicate_title_failure(session, create_blog_post):
    """Verifies that creating a duplicate post fails (raising BlogPostDuplicateError)."""
    repository = BlogPostRepository(session)

    # Arrange: Create the first post with a specific title
    create_blog_post(title="Duplicate Title", drive_file_id="unique-file-id")
    session.commit()

    # Act & Assert: Expect BlogPostDuplicateError on duplicate title
    with pytest.raises(BlogPostDuplicateError):
        repository.create_blog_post(
            title="Duplicate Title",
            content="Duplicate title content",
            drive_file_id="new-unique-file-id"
        )


def test_create_blog_post_failure(session, monkeypatch):
    """Verifies behavior when a SQLAlchemy error occurs during blog post creation."""
    repository = BlogPostRepository(session)
    monkeypatch.setattr(session, 'execute',
                        lambda *args, **kwargs: (_ for _ in ()).throw(
                            SQLAlchemyError()))

    # Act & Assert: RuntimeError should be raised due to SQLAlchemyError
    with pytest.raises(RuntimeError,
                       match="Failed to create blog post in the database."):
        repository.create_blog_post(
            title='Fail Title',
            content='Fail Content',
            drive_file_id='fail-drive-file-id'
        )


def test_create_blog_post_missing_content(session):
    """Verifies that creating a blog post with missing content raises IntegrityError."""
    repository = BlogPostRepository(session)

    # Act and Assert: Attempt to create the blog post without content
    with pytest.raises(IntegrityError, match="NOT NULL constraint failed: blog_posts.content"):
        repository.create_blog_post(
            title='Missing Content Post',
            content=None,  # type: ignore
            drive_file_id='missing-content-file-id'
        )


def test_create_blog_post_with_excessively_long_content(session):
    """Verifies that overly long blog post content raises a RuntimeError."""
    repository = BlogPostRepository(session)
    long_content = 'A' * 1000000000  # Very long content

    with pytest.raises(RuntimeError, match="Failed to create blog post"):
        repository.create_blog_post(
            title='Excessively Long Content Post',
            content=long_content,
            drive_file_id='long-content-file-id'
        )


@pytest.mark.parametrize("post_count", [1, 2, 5, 10])
def test_create_multiple_blog_posts(session, create_blog_post, post_count):
    """Verifies successful creation of multiple blog posts."""
    repository = BlogPostRepository(session)

    # Arrange: Create blog posts using the fixture
    for i in range(post_count):
        create_blog_post(
            title=f"Post {i + 1}",
            content=f"Content {i + 1}",
            drive_file_id=f"file-id-{i + 1}"
        )
    session.commit()

    # Act: Fetch all blog posts
    posts = repository.fetch_all_blog_posts()

    # Assert: Verify the number of blog posts and their content
    assert len(posts) == post_count
    for i in range(post_count):
        assert posts[i].title == f"Post {i + 1}"
        assert posts[i].content == f"Content {i + 1}"


def test_fetch_blog_posts_empty_db(session):
    """Verifies that fetching all blog posts returns an empty list when the database is empty."""
    repository = BlogPostRepository(session)

    # Act: Fetch all blog posts from an empty database
    posts = repository.fetch_all_blog_posts()

    # Assert: The result should be an empty list
    assert posts == []
