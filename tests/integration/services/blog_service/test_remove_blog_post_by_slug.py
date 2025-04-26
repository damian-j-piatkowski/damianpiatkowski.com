"""Integration tests for the remove_blog_post_by_slug service function.

This module contains integration tests for the remove_blog_post_by_slug function
of the blog_service module, verifying its behavior in orchestrating the deletion
of blog posts from the database by slug.

Tests included:
    - test_remove_blog_post_by_slug_existing_post: Removes an existing blog post successfully.
    - test_remove_blog_post_by_slug_multiple_calls: Ensures multiple removals fail gracefully.
    - test_remove_blog_post_by_slug_nonexistent_slug: Raises appropriate error for missing slug.

Fixtures:
    - create_blog_post: Creates an individual blog post.
    - session: Provides a database session.
"""

import pytest

from app.exceptions import BlogPostNotFoundError
from app.models.repositories.blog_post_repository import BlogPostRepository
from app.services.blog_service import remove_blog_post_by_slug


@pytest.mark.admin_delete_blog_posts
def test_remove_blog_post_by_slug_existing_post(session, create_blog_post):
    """Removes an existing blog post successfully."""
    create_blog_post("Post to Remove", "remove-this", "Temporary content", "temp_drive_id")
    session.commit()

    remove_blog_post_by_slug("remove-this")

    repository = BlogPostRepository(session)
    with pytest.raises(BlogPostNotFoundError):
        repository.fetch_blog_post_by_slug("remove-this")


@pytest.mark.admin_delete_blog_posts
def test_remove_blog_post_by_slug_multiple_calls(session, create_blog_post):
    """Ensures multiple removals fail gracefully after the first successful removal."""
    create_blog_post("Remove Only Once", "remove-once", "One-time content", "drive_id_once")
    session.commit()

    remove_blog_post_by_slug("remove-once")

    with pytest.raises(BlogPostNotFoundError):
        remove_blog_post_by_slug("remove-once")


@pytest.mark.admin_delete_blog_posts
def test_remove_blog_post_by_slug_nonexistent_slug(session):
    """Raises appropriate error when attempting to remove a non-existent post."""
    with pytest.raises(BlogPostNotFoundError, match="No blog post found with slug nonexistent-slug"):
        remove_blog_post_by_slug("nonexistent-slug")
