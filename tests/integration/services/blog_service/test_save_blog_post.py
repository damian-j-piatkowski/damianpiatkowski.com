"""Integration tests for the save_blog_post service function.

This module contains integration tests for the save_blog_post service,
focusing on interactions with the in-memory database. The tests verify that the
service correctly saves blog posts under various conditions.

Tests included:
    - test_save_blog_post_success: Verifies that a valid blog post is saved correctly.
    - test_save_blog_post_missing_fields: Ensures that missing required fields
      raise an appropriate error.
    - test_save_blog_post_duplicate_url: Checks that saving a blog post with a
      duplicate URL raises an IntegrityError.

Fixtures:
    - create_blog_post: Fixture to create blog posts in the database.
    - session: Provides a session object for database interactions.
"""

import pytest
from sqlalchemy.exc import IntegrityError

from app.services.blog_service import save_blog_post, fetch_all_blog_posts


def test_save_blog_post_success(session) -> None:
    """Integration test for save_blog_post service with valid data.

    This test verifies that a valid blog post is saved correctly and returns
    the expected data.
    """
    # Arrange: Create a dictionary with valid blog post data
    valid_data = {
        'title': "First Post",
        'content': "Content for the first post.",
        'image_small': "path/to/small.jpg",
        'image_medium': "path/to/medium.jpg",
        'image_large': "path/to/large.jpg",
        'url': "http://example.com/first-post"
    }

    # Act: Save the blog post using the service function
    saved_post = save_blog_post(valid_data)

    # Assert: Validate that the saved post data matches the input
    assert saved_post['title'] == valid_data['title']
    assert saved_post['content'] == valid_data['content']
    assert saved_post['image_small'] == valid_data['image_small']
    assert saved_post['image_medium'] == valid_data['image_medium']
    assert saved_post['image_large'] == valid_data['image_large']
    assert saved_post['url'] == valid_data['url']


def test_save_blog_post_missing_fields(session) -> None:
    """Integration test for save_blog_post service with missing required fields.

    This test ensures that providing incomplete data raises a KeyError.
    """
    # Arrange: Create a dictionary with missing fields
    incomplete_data = {
        'title': "Incomplete Post",
        'content': "Content for the incomplete post.",
        # Missing image fields and URL
    }

    # Act & Assert: Ensure that calling the service function raises a KeyError
    with pytest.raises(KeyError) as exc_info:
        save_blog_post(incomplete_data)

    # Assert: Check that the raised KeyError message mentions a missing key
    assert any(field in str(exc_info.value) for field in
               ['image_small', 'image_medium', 'image_large', 'url']), \
        "Expected KeyError for missing required fields."


def test_save_blog_post_duplicate_url(session, create_blog_post) -> None:
    """Integration test for save_blog_post service with a duplicate URL.

    This test checks that attempting to save a blog post with a duplicate URL
    raises an IntegrityError.
    """
    # Arrange: Create the first blog post with a unique URL
    initial_data = {
        'title': "First Post",
        'content': "Content for the first post.",
        'image_small': "path/to/small.jpg",
        'image_medium': "path/to/medium.jpg",
        'image_large': "path/to/large.jpg",
        'url': "http://example.com/duplicate-url"
    }

    # Create and commit the first blog post
    post1 = create_blog_post(**initial_data)
    session.commit()  # Commit the transaction to save the first post

    # Arrange: Create a second blog post with the same URL
    duplicate_data = {
        'title': "Second Post",
        'content': "Content for the second post.",
        'image_small': "path/to/small.jpg",
        'image_medium': "path/to/medium.jpg",
        'image_large': "path/to/large.jpg",
        'url': "http://example.com/duplicate-url"  # Duplicate URL
    }

    # Act & Assert: Ensure that calling the service function raises an IntegrityError
    with pytest.raises(IntegrityError):
        save_blog_post(duplicate_data)


