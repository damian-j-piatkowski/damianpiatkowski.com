"""Integration tests for the fetch_all_blog_posts service function.

This module contains integration tests for the fetch_all_blog_posts service,
focusing on interactions with the in-memory database. The tests verify that the
service correctly retrieves blog posts under various conditions.

Tests included:
    - test_fetch_all_blog_posts: Verifies that the service fetches multiple
      blog posts correctly.
    - test_fetch_all_blog_posts_empty: Ensures that the service returns an
      empty list when no blog posts exist.
    - test_fetch_all_blog_posts_multiple: Checks the service behavior when
      many blog posts are present in the database.
    - test_fetch_all_blog_posts_database_error: Simulates a database error
      and checks if the service raises the appropriate exception.

Fixtures:
    - create_blog_post: Fixture to create blog posts in the database.
    - session: Provides a session object for database interactions.
"""

import pytest

from app.services.blog_service import fetch_all_blog_posts


def test_fetch_all_blog_posts(session, create_blog_post) -> None:
    """Integration test for fetch_all_blog_posts service.

    This test uses the in-memory database and the create_blog_post fixture
    to insert blog posts into the database and ensure that the service fetches
    them correctly.
    """
    # Arrange: Create and add a few blog posts using the create_blog_post fixture
    create_blog_post(
        title="First Post",
        content="Content for the first post.",
        url="http://example.com/first-post"
    )
    create_blog_post(
        title="Second Post",
        content="Content for the second post.",
        url="http://example.com/second-post"
    )
    session.commit()  # Commit the posts to the in-memory database

    # Act: Fetch all blog posts using the service function
    fetched_posts = fetch_all_blog_posts()

    # Assert: Validate that the correct number of posts were fetched
    assert len(fetched_posts) == 2

    # Assert: Validate that the posts have the correct content
    assert fetched_posts[0]['title'] == "First Post"
    assert fetched_posts[1]['title'] == "Second Post"


def test_fetch_all_blog_posts_empty(session) -> None:
    """Integration test for fetch_all_blog_posts service when there are no blog posts.

    This test ensures that the service correctly returns an empty list when no
    blog posts exist.
    """
    # Act: Fetch all blog posts using the service function
    fetched_posts = fetch_all_blog_posts()

    # Assert: Validate that the result is an empty list
    assert fetched_posts == []


def test_fetch_all_blog_posts_multiple(session, create_blog_post) -> None:
    """Integration test for fetch_all_blog_posts service with multiple blog posts.

    This test checks the service behavior when many blog posts are present in
    the database.
    """
    # Arrange: Create and add multiple blog posts using the create_blog_post fixture
    for i in range(30):
        create_blog_post(
            title=f"Post {i + 1}",
            content=f"Content for post {i + 1}.",
            url=f"http://example.com/post-{i + 1}"
        )
    session.commit()  # Commit the posts to the in-memory database

    # Act: Fetch all blog posts using the service function
    fetched_posts = fetch_all_blog_posts()

    # Assert: Validate that the correct number of posts were fetched
    assert len(fetched_posts) == 30


def test_fetch_all_blog_posts_database_error(session, mocker) -> None:
    """Integration test for fetch_all_blog_posts service to check error handling.

    This test simulates a database error and checks if the service raises the
    appropriate exception.
    """
    # Arrange: Mock the session to raise a SQLAlchemyError
    mocker.patch('app.extensions.db.session.execute', side_effect=RuntimeError("Database error"))

    # Act & Assert: Ensure that calling the service function raises a RuntimeError
    with pytest.raises(RuntimeError, match="Failed to retrieve blog posts"):
        fetch_all_blog_posts()
