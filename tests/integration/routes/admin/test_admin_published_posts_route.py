"""Integration tests for the /admin/published-posts route.

This module verifies the integration between the Flask route /admin/published-posts
and the get_published_blog_posts controller. It checks how the route responds to
different data conditions in the database and ensures correct formatting of returned data.

Test Functions:
    - test_published_posts_handles_internal_error
    - test_published_posts_returns_correct_structure
    - test_published_posts_returns_empty_list_when_no_posts
    - test_published_posts_returns_multiple_posts

Fixtures:
    - app: Flask app context.
    - client: Flask test client for making requests.
    - session: SQLAlchemy session for DB state.
    - create_blog_post: Factory for creating published blog post records.
    - mocker: Used to patch controller behavior in error scenarios.
"""

import pytest


@pytest.mark.admin_published_posts
def test_published_posts_handles_internal_error(app, client, mocker):
    """Verifies that the route returns a 500 error when an unexpected exception occurs in the controller."""
    with app.app_context():
        mocker.patch(
            "app.controllers.admin_controller.get_all_blog_post_identifiers",
            side_effect=Exception("Unexpected DB error")
        )
        response = client.get("/admin/published-posts")
        assert response.status_code == 500
        assert response.get_json() == {"error": "Unexpected DB error"}


@pytest.mark.admin_published_posts
def test_published_posts_returns_correct_structure(client, session, create_blog_post):
    """Verifies that a single published blog post is returned in the correct structure."""
    create_blog_post(
        title="Test Post",
        slug="test-post",
        content="Some content",
        drive_file_id="abc123"
    )
    session.commit()

    response = client.get("/admin/published-posts")
    assert response.status_code == 200
    posts = response.get_json()

    assert isinstance(posts, list)
    assert len(posts) == 1
    assert posts[0]["slug"] == "test-post"
    assert posts[0]["title"] == "Test Post"
    assert posts[0]["id"] == "abc123"


@pytest.mark.admin_published_posts
def test_published_posts_returns_empty_list_when_no_posts(client, session):
    """Verifies that the route returns an empty list when there are no blog posts in the database."""
    response = client.get("/admin/published-posts")
    assert response.status_code == 200
    assert response.get_json() == []


@pytest.mark.admin_published_posts
@pytest.mark.parametrize("post_count", [2, 10, 30])
def test_published_posts_returns_multiple_posts(client, session, seed_blog_posts, post_count):
    """Verifies that the route returns the correct number of posts and expected structure across multiple counts."""
    created_posts = seed_blog_posts(post_count)
    session.commit()

    response = client.get("/admin/published-posts")
    assert response.status_code == 200

    posts = response.get_json()
    assert isinstance(posts, list)
    assert len(posts) == post_count

    for i, post in enumerate(posts):
        assert post["slug"] == created_posts[i].slug
        assert post["title"] == created_posts[i].title
        assert post["id"] == created_posts[i].drive_file_id

