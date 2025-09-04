"""Integration tests for the get_published_blog_posts controller function.

This module contains integration tests for the get_published_blog_posts
controller function, verifying behavior in response to various database
states and service-level exceptions.

Tests included:
    - test_handles_internal_error_gracefully: Validates handling of an unexpected exception.
    - test_handles_runtime_error_from_service: Verifies propagation of a known service-level RuntimeError.
    - test_returns_correct_number_of_published_posts: Ensures correct output for varying numbers of blog posts.
    - test_returns_empty_list_when_no_published_posts: Confirms the controller returns an
        empty list when no posts exist.

Fixtures:
    - app: Provides the Flask application context for the tests.
    - mocker: Provides mocking utilities for simulating service errors.
    - seed_blog_posts: Factory fixture to create N blog posts in the database.
    - session: Provides SQLAlchemy session access to the in-memory database.
"""

from typing import List

import pytest

from app.controllers.admin_controller import get_published_blog_posts
from app.domain.blog_post import BlogPost


@pytest.mark.admin_published_posts
@pytest.mark.parametrize("post_count", [2, 10, 30])
def test_returns_correct_number_of_published_posts(app, session, seed_blog_posts, post_count):
    """Test that the correct number of blog posts is returned for varying post counts."""
    with app.app_context():
        created_posts: List[BlogPost] = seed_blog_posts(post_count)
        session.commit()

        response, status_code = get_published_blog_posts()
        data = response.get_json()

        assert status_code == 200
        assert isinstance(data, list)
        assert len(data) == post_count

        # Ensure all returned fields match expectations
        for i, item in enumerate(data):
            assert item["slug"] == created_posts[i].slug
            assert item["title"] == created_posts[i].title
            assert item["id"] == created_posts[i].drive_file_id


@pytest.mark.admin_published_posts
def test_handles_internal_error_gracefully(app, session, mocker):
    """Test that an internal error returns a 500 status code and error message."""
    with app.app_context():
        mocker.patch("app.controllers.admin_controller.get_all_blog_post_identifiers",
                     side_effect=Exception("Unexpected DB error"))

        response, status_code = get_published_blog_posts()
        data = response.get_json()

        assert status_code == 500
        assert "error" in data
        assert "Unexpected DB error" in data["error"]


@pytest.mark.admin_published_posts
def test_handles_runtime_error_from_service(app, session, mocker):
    """Test that a RuntimeError raised by the service is handled and returns 500."""
    with app.app_context():
        mocker.patch("app.controllers.admin_controller.get_all_blog_post_identifiers",
                     side_effect=RuntimeError("Repository failure"))

        response, status_code = get_published_blog_posts()
        data = response.get_json()

        assert status_code == 500
        assert "error" in data
        assert "Repository failure" in data["error"]


@pytest.mark.admin_published_posts
def test_returns_empty_list_when_no_published_posts(app, session):
    """Test that an empty list is returned when there are no blog posts."""
    with app.app_context():
        response, status_code = get_published_blog_posts()
        data = response.get_json()

        assert status_code == 200
        assert data == []
