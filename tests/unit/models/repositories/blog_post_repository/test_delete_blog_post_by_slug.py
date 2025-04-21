"""Unit tests for the delete_blog_post_by_slug repository method.

This module contains unit tests for the delete_blog_post_by_slug method of
the BlogPostRepository class, verifying its behavior in removing blog posts
from the database by slug.

Tests included:
    - test_delete_blog_post_by_slug_existing_post: Deletes an existing blog post.
    - test_delete_blog_post_by_slug_multiple_calls: Ensures multiple deletions fail gracefully.
    - test_delete_blog_post_by_slug_nonexistent_slug: Raises appropriate error for missing slug.

Fixtures:
    - create_blog_post: Creates an individual blog post.
    - session: Provides a database session.
"""

import pytest

from app.exceptions import BlogPostNotFoundError
from app.models.repositories.blog_post_repository import BlogPostRepository


@pytest.mark.admin_delete_blog_posts
def test_delete_blog_post_by_slug_existing_post(session, create_blog_post):
    """Deletes an existing blog post."""
    create_blog_post("Post to Delete", "delete-this", "Temporary content", "temp_drive_id")
    session.commit()
    repository = BlogPostRepository(session)

    repository.delete_blog_post_by_slug("delete-this")
    session.commit()

    with pytest.raises(BlogPostNotFoundError):
        repository.fetch_blog_post_by_slug("delete-this")


@pytest.mark.admin_delete_blog_posts
def test_delete_blog_post_by_slug_multiple_calls(session, create_blog_post):
    """Ensures multiple deletions fail gracefully after the first successful deletion."""
    create_blog_post("Only Delete Once", "delete-once", "One-time content", "drive_id_once")
    session.commit()
    repository = BlogPostRepository(session)

    repository.delete_blog_post_by_slug("delete-once")
    session.commit()

    with pytest.raises(BlogPostNotFoundError):
        repository.delete_blog_post_by_slug("delete-once")


@pytest.mark.admin_delete_blog_posts
def test_delete_blog_post_by_slug_nonexistent_slug(session):
    """Raises appropriate error when attempting to delete a non-existent post."""
    repository = BlogPostRepository(session)

    with pytest.raises(BlogPostNotFoundError, match="No blog post found with slug nonexistent-slug"):
        repository.delete_blog_post_by_slug("nonexistent-slug")
