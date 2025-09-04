"""Unit tests for the fetch_blog_post_by_slug repository method.

This module contains unit tests for the fetch_blog_post_by_slug method of
the BlogPostRepository class, verifying its behavior in retrieving individual
blog posts from the database.

Tests included:
    - test_fetch_blog_post_by_slug_long_content: Handles very long content.
    - test_fetch_blog_post_by_slug_missing_drive_file_id: Ensures it works when drive_file_id is None.
    - test_fetch_blog_post_by_slug_not_found: Ensures proper handling when post does not exist.
    - test_fetch_blog_post_by_slug_special_characters: Handles titles and content with special characters.
    - test_fetch_blog_post_by_slug_valid: Ensures retrieval of an existing post.

Fixtures:
    - create_blog_post: Function fixture to create individual blog posts with custom attributes.
    - session: Provides a database session.
"""

import pytest

from app.exceptions import BlogPostNotFoundError
from app.models.repositories.blog_post_repository import BlogPostRepository


@pytest.mark.render_single_blog_post
def test_fetch_blog_post_by_slug_long_content(session, create_blog_post):
    """Handles very long content fields."""
    long_content = "<p>" + ("This is some <b>formatted</b> text with <i>various</i> tags. " * 100) + "</p>"
    post = create_blog_post(title="Long Content Post", slug="long-content-post", html_content=long_content)
    session.commit()
    repository = BlogPostRepository(session)

    retrieved_post = repository.fetch_blog_post_by_slug(post.slug)

    assert retrieved_post.title == "Long Content Post"
    assert retrieved_post.html_content == long_content


@pytest.mark.render_single_blog_post
def test_fetch_blog_post_by_slug_not_found(session):
    """Ensures an error is raised when attempting to retrieve a non-existent blog post."""
    repository = BlogPostRepository(session)

    with pytest.raises(BlogPostNotFoundError, match="No blog post found with slug non-existent-slug"):
        repository.fetch_blog_post_by_slug("non-existent-slug")


@pytest.mark.render_single_blog_post
def test_fetch_blog_post_by_slug_special_characters(session, create_blog_post):
    """Handles titles and content with special characters."""
    post = create_blog_post(title="Spécîål 💡 Tîtle", slug="special-title", html_content="Côntênt with 🎉 emojis & symbols!")
    session.commit()
    repository = BlogPostRepository(session)

    retrieved_post = repository.fetch_blog_post_by_slug(post.slug)

    assert retrieved_post.title == "Spécîål 💡 Tîtle"
    assert retrieved_post.html_content == "Côntênt with 🎉 emojis & symbols!"


@pytest.mark.render_single_blog_post
def test_fetch_blog_post_by_slug_valid(session, create_blog_post):
    """Ensures a blog post can be retrieved by its slug."""
    post = create_blog_post(title="Valid Post", slug="valid-post", html_content="<p>Valid content</p>", drive_file_id="drive123")
    session.commit()
    repository = BlogPostRepository(session)

    retrieved_post = repository.fetch_blog_post_by_slug(post.slug)

    assert retrieved_post.title == "Valid Post"
    assert retrieved_post.html_content == "<p>Valid content</p>"
    assert retrieved_post.drive_file_id == "drive123"
