"""Integration tests for the get_paginated_posts controller function.

This module contains integration tests for the get_paginated_posts function,
verifying its behavior in retrieving paginated blog posts and returning JSON responses.

Tests included:
    - test_get_paginated_posts_custom_per_page: Ensures pagination works with non-default per_page values.
    - test_get_paginated_posts_empty: Ensures that requesting pagination when no posts exist returns a 404 response.
    - test_get_paginated_posts_invalid_page: Checks that requesting page=0 or negative page numbers defaults to page 1.
    - test_get_paginated_posts_multiple_pages: Verifies pagination across multiple pages, ensuring correct ordering.
    - test_get_paginated_posts_multiple_pages_custom_per_page: Verifies pagination with custom per_page values.
    - test_get_paginated_posts_out_of_range: Ensures requesting a page beyond the total available pages
        returns an empty list.
    - test_get_paginated_posts_single_page: Verifies pagination when all posts fit within a single page.

Fixtures:
    - seed_blog_posts: Fixture to seed blog posts in the database.
    - session: Provides a session object for database interactions.
"""

import pytest
from freezegun import freeze_time

from app.controllers.blog_controller import get_paginated_posts
from tests.fixtures.blog_data_fixtures import seed_blog_posts


@pytest.mark.render_blog_posts
def test_get_paginated_posts_custom_per_page(session, seed_blog_posts):
    """Ensures pagination works with non-default per_page values."""
    seed_blog_posts(20)
    session.commit()

    response, status_code = get_paginated_posts(page=1, per_page=5)
    json_data = response.get_json()

    assert status_code == 200
    assert len(json_data["posts"]) == 5
    assert json_data["total_pages"] == 4
    assert "slug" in json_data["posts"][0]  # Verify slug is included


@pytest.mark.render_blog_posts
def test_get_paginated_posts_empty(session):
    """Ensures requesting pagination when no posts exist returns a 404 response."""
    response, status_code = get_paginated_posts(page=1, per_page=10)
    json_data = response.get_json()

    assert status_code == 404
    assert json_data == {"message": "No blog posts found"}


@pytest.mark.render_blog_posts
@freeze_time("2024-12-04 14:18:16")
def test_get_paginated_posts_invalid_page(session, seed_blog_posts):
    """Checks that requesting page=0 or negative page numbers defaults to page 1."""
    seed_blog_posts(2)
    session.commit()

    response_zero, _ = get_paginated_posts(page=0, per_page=10)
    response_negative, _ = get_paginated_posts(page=-5, per_page=10)

    assert response_zero.get_json() == response_negative.get_json()
    assert len(response_zero.get_json()["posts"]) == 2
    assert response_zero.get_json()["total_pages"] == 1


@pytest.mark.render_blog_posts
def test_get_paginated_posts_multiple_pages(session, seed_blog_posts):
    """Verifies pagination across multiple pages, ensuring correct ordering."""
    seed_blog_posts(32)
    session.commit()

    response_page_1, _ = get_paginated_posts(page=1, per_page=10)
    response_page_2, _ = get_paginated_posts(page=2, per_page=10)
    response_page_3, _ = get_paginated_posts(page=3, per_page=10)
    response_page_4, _ = get_paginated_posts(page=4, per_page=10)

    assert len(response_page_1.get_json()["posts"]) == 10
    assert len(response_page_2.get_json()["posts"]) == 10
    assert len(response_page_3.get_json()["posts"]) == 10
    assert len(response_page_4.get_json()["posts"]) == 2
    assert response_page_1.get_json()["posts"][0]["title"] == "Post 1"
    assert response_page_1.get_json()["posts"][0]["slug"] == "post-1"
    assert response_page_2.get_json()["posts"][0]["title"] == "Post 11"
    assert response_page_2.get_json()["posts"][0]["slug"] == "post-11"


@pytest.mark.render_blog_posts
def test_get_paginated_posts_multiple_pages_custom_per_page(session, seed_blog_posts):
    """Verifies pagination with custom per_page values."""
    seed_blog_posts(25)
    session.commit()

    response_page_1, _ = get_paginated_posts(page=1, per_page=7)
    response_page_2, _ = get_paginated_posts(page=2, per_page=7)
    response_page_3, _ = get_paginated_posts(page=3, per_page=7)
    response_page_4, _ = get_paginated_posts(page=4, per_page=7)

    assert len(response_page_1.get_json()["posts"]) == 7
    assert len(response_page_2.get_json()["posts"]) == 7
    assert len(response_page_3.get_json()["posts"]) == 7
    assert len(response_page_4.get_json()["posts"]) == 4
    assert response_page_1.get_json()["posts"][0]["slug"] == "post-1"


@pytest.mark.render_blog_posts
def test_get_paginated_posts_out_of_range(session, seed_blog_posts):
    """Ensures requesting a page beyond the total available pages returns a 404."""
    seed_blog_posts(15)
    session.commit()

    response, status_code = get_paginated_posts(page=5, per_page=10)
    json_data = response.get_json()

    assert status_code == 404
    assert json_data == {"message": "No blog posts found"}


@pytest.mark.render_blog_posts
def test_get_paginated_posts_single_page(session, seed_blog_posts):
    """Verifies pagination when all posts fit within a single page."""
    seed_blog_posts(7)
    session.commit()

    response, status_code = get_paginated_posts(page=1, per_page=10)
    json_data = response.get_json()

    assert status_code == 200
    assert len(json_data["posts"]) == 7
    assert json_data["total_pages"] == 1
    assert json_data["posts"][0]["title"] == "Post 1"
    assert json_data["posts"][0]["slug"] == "post-1"
    assert json_data["posts"][-1]["title"] == "Post 7"
    assert json_data["posts"][-1]["slug"] == "post-7"
