"""Integration tests for the get_blog_post service function.

This module contains integration tests for the get_blog_post service,
verifying its behavior when retrieving a single blog post from the database.

Tests included:
    - test_get_blog_post_case_sensitivity: Checks if slug lookup is case-sensitive (based on database behavior).
    - test_get_blog_post_existing: Ensures that fetching an existing blog post by slug returns the correct post.
    - test_get_blog_post_multiple_similar_slugs: Verifies fetching a specific slug when multiple similar slugs exist.
    - test_get_blog_post_nonexistent: Ensures that fetching a non-existent blog post raises BlogPostNotFoundError.
    - test_get_blog_post_slug_trailing_spaces: Ensures lookup remains consistent when slugs have accidental spaces.

Fixtures:
    - seed_blog_posts: Fixture to create blog posts in the database.
    - session: Provides a session object for database interactions.
"""

import pytest

from app.exceptions import BlogPostNotFoundError
from app.services.blog_service import get_blog_post


@pytest.mark.render_single_blog_post
def test_get_blog_post_case_sensitivity(session, seed_blog_posts) -> None:
    """Checks if slug lookup is case-sensitive (based on database behavior)."""
    posts = seed_blog_posts(1)
    session.commit()

    mixed_case_slug = posts[0].slug.upper()  # Modify slug case

    with pytest.raises(BlogPostNotFoundError):
        get_blog_post(mixed_case_slug)


@pytest.mark.render_single_blog_post
def test_get_blog_post_existing(session, seed_blog_posts) -> None:
    """Ensures that fetching an existing blog post by slug returns the correct post."""
    posts = seed_blog_posts(1)
    session.commit()

    post = get_blog_post(posts[0].slug)

    assert post is not None
    assert post.title == posts[0].title
    assert post.slug == posts[0].slug
    assert post.html_content == posts[0].html_content
    assert post.drive_file_id == posts[0].drive_file_id


@pytest.mark.render_single_blog_post
def test_get_blog_post_multiple_similar_slugs(session, seed_blog_posts) -> None:
    """Verifies fetching a specific slug when multiple similar slugs exist."""
    posts = seed_blog_posts(2)
    session.commit()

    post = get_blog_post(posts[1].slug)

    assert post is not None
    assert post.slug == posts[1].slug


@pytest.mark.render_single_blog_post
def test_get_blog_post_nonexistent(session) -> None:
    """Ensures that fetching a non-existent blog post raises BlogPostNotFoundError."""
    with pytest.raises(BlogPostNotFoundError, match="No blog post found with slug nonexistent-slug"):
        get_blog_post("nonexistent-slug")


@pytest.mark.render_single_blog_post
def test_get_blog_post_slug_trailing_spaces(session, seed_blog_posts) -> None:
    """Ensures lookup remains consistent when slugs have accidental spaces."""
    posts = seed_blog_posts(1)
    session.commit()

    with pytest.raises(BlogPostNotFoundError, match=f"No blog post found with slug  {posts[0].slug} "):
        get_blog_post(f" {posts[0].slug} ")  # Add spaces around slug
