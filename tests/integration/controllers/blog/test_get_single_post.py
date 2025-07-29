"""Integration tests for the get_single_post controller function.

This module contains integration tests for the get_single_post function,
verifying its behavior in retrieving a single blog post and returning a JSON response.

Tests included:
    - test_get_single_post_case_sensitivity: Ensures slug lookup is case-sensitive.
    - test_get_single_post_nonexistent: Ensures that fetching a non-existent blog post returns a 404 response.
    - test_get_single_post_slug_trailing_spaces: Ensures slugs with leading/trailing spaces return a 404 response.
    - test_get_single_post_success: Verifies that retrieving an existing blog post returns the expected data.

Fixtures:
    - seed_blog_posts: Fixture to create blog posts in the database.
    - session: Provides a session object for database interactions.
"""

from datetime import datetime, timedelta, UTC

import pytest

from app.controllers.blog_controller import get_single_post
from tests.fixtures.blog_data_fixtures import seed_blog_posts


@pytest.mark.render_single_blog_post
def test_get_single_post_case_sensitivity(session, seed_blog_posts) -> None:
    """Ensures slug lookup is case-sensitive."""
    seed_blog_posts(1)
    session.commit()

    response_upper, status_upper = get_single_post("POST-1")
    response_mixed, status_mixed = get_single_post("PoSt-1")

    assert status_upper == 404
    assert status_mixed == 404


@pytest.mark.render_single_blog_post
def test_get_single_post_nonexistent(session) -> None:
    """Ensures that fetching a non-existent blog post returns a 404 response."""
    response, status_code = get_single_post("nonexistent-slug")
    json_data = response.get_json()

    assert status_code == 404
    assert json_data == {"message": "Blog post not found"}


@pytest.mark.render_single_blog_post
def test_get_single_post_slug_trailing_spaces(session, seed_blog_posts) -> None:
    """Ensures slugs with leading/trailing spaces return a 404 response."""
    seed_blog_posts(1)
    session.commit()

    response, status_code = get_single_post(" post-1 ")

    assert status_code == 404


@pytest.mark.render_single_blog_post
def test_get_single_post_success(session, seed_blog_posts) -> None:
    """Verifies that retrieving an existing blog post returns the expected data."""
    posts = seed_blog_posts(1)
    session.commit()

    expected_post = posts[0]
    response, status_code = get_single_post(expected_post.slug)
    json_data = response.get_json()

    assert status_code == 200

    # 1. Check that created_at exists and is recent
    created_at_str = json_data.pop("created_at", None)
    assert created_at_str is not None, "created_at field is missing"
    created_at = datetime.strptime(created_at_str, "%Y-%m-%d %H:%M:%S")

    # Ensure created_at is timezone-aware (UTC)
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=UTC)

    assert datetime.now(UTC) - created_at < timedelta(minutes=1), "created_at is not recent"

    # 2. Compare the remaining fields
    assert json_data == {
        "title": expected_post.title,
        "slug": expected_post.slug,
        "html_content": expected_post.html_content,
        "drive_file_id": expected_post.drive_file_id,
        "categories": [],
        "hero_base": "/static/blog-images/default/hero",
    }
