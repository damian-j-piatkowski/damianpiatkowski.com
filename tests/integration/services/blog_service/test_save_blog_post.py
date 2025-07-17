"""Integration tests for the save_blog_post service function.

This module contains integration tests for the save_blog_post service,
focusing on interactions with the in-memory database. The tests verify that the
service correctly saves blog posts under various conditions.

Tests included:
    - test_save_blog_post_duplicate_drive_file_id: Ensures saving a blog post with a
      duplicate drive_file_id raises a BlogPostDuplicateError.
    - test_save_blog_post_duplicate_slug: Ensures saving a blog post with a duplicate
      slug raises a BlogPostDuplicateError.
    - test_save_blog_post_duplicate_title: Ensures saving a blog post with a duplicate
      title raises a BlogPostDuplicateError.
    - test_save_blog_post_missing_fields: Ensures missing required fields raise a KeyError.
    - test_save_blog_post_success: Verifies that a valid blog post is saved correctly.

Fixtures:
    - create_blog_post: Fixture to create blog posts in the database.
    - session: Provides a session object for database interactions.
"""

import pytest

from app.domain.blog_post import BlogPost
from app.exceptions import BlogPostDuplicateError
from app.services.blog_service import save_blog_post


@pytest.mark.admin_upload_blog_posts
def test_save_blog_post_duplicate_drive_file_id(session, create_blog_post) -> None:
    """Integration test for save_blog_post service with a duplicate drive file ID.

    This test checks that attempting to save a blog post with a duplicate drive file ID
    raises a BlogPostDuplicateError.
    """
    # Arrange: Create the first blog post with a unique drive file ID
    initial_data = {
        'title': "First Post",
        'slug': "first-post",
        'html_content': "<p>Content for the first post.</p>",
        'drive_file_id': "unique_drive_file_id_1"
    }

    # Create and commit the first blog post
    create_blog_post(**initial_data)
    session.commit()  # Commit the transaction to save the first post

    # Arrange: Create a second blog post with the same drive file ID
    duplicate_data = {
        'title': "Second Post",
        'slug': "second-post",
        'html_content': "<p>Content for the second post.</p>",
        'drive_file_id': "unique_drive_file_id_1"  # Duplicate drive_file_id
    }

    # Act & Assert: Ensure that calling the service function raises a BlogPostDuplicateError
    with pytest.raises(BlogPostDuplicateError) as exc_info:
        save_blog_post(duplicate_data)

    assert exc_info.value.field_name == 'drive_file_id'
    assert exc_info.value.field_value == 'unique_drive_file_id_1'
    assert exc_info.value.message == "A blog post with this drive_file_id already exists."


@pytest.mark.admin_upload_blog_posts
def test_save_blog_post_duplicate_slug(session, create_blog_post) -> None:
    """Integration test for save_blog_post service with a duplicate slug.

    This test checks that attempting to save a blog post with a duplicate slug
    raises a BlogPostDuplicateError.
    """
    # Arrange: Create the first blog post with a unique slug
    initial_data = {
        'title': "First Post",
        'slug': "first-post",
        'html_content': "<p>Content for the first post.</p>",
        'drive_file_id': "unique_drive_file_id_1"
    }

    # Create and commit the first blog post
    create_blog_post(**initial_data)
    session.commit()  # Commit the transaction to save the first post

    # Arrange: Create a second blog post with the same slug
    duplicate_data = {
        'title': "Second Post",
        'slug': "first-post",  # Duplicate slug
        'html_content': "<p>Content for the second post.</p>",
        'drive_file_id': "unique_drive_file_id_2"
    }

    # Act & Assert: Ensure that calling the service function raises a BlogPostDuplicateError
    with pytest.raises(BlogPostDuplicateError) as exc_info:
        save_blog_post(duplicate_data)

    assert exc_info.value.field_name == 'slug'
    assert exc_info.value.field_value == 'first-post'
    assert exc_info.value.message == "A blog post with this slug already exists."


@pytest.mark.admin_upload_blog_posts
def test_save_blog_post_duplicate_title(session, create_blog_post) -> None:
    """Integration test for save_blog_post service with a duplicate title.

    This test checks that attempting to save a blog post with a duplicate title
    raises a BlogPostDuplicateError.
    """
    # Arrange: Create the first blog post with a unique title
    initial_data = {
        'title': "First Post",
        'slug': "first-post",
        'html_content': "<p>Content for the first post.</p>",
        'drive_file_id': "unique_drive_file_id_1"
    }

    # Create and commit the first blog post
    create_blog_post(**initial_data)
    session.commit()  # Commit the transaction to save the first post

    # Arrange: Create a second blog post with the same title
    duplicate_data = {
        'title': "First Post",  # Duplicate title
        'slug': "first-post-duplicate",
        'html_content': "<p>Content for the second post.</p>",
        'drive_file_id': "unique_drive_file_id_2"
    }

    # Act & Assert: Ensure that calling the service function raises a BlogPostDuplicateError
    with pytest.raises(BlogPostDuplicateError) as exc_info:
        save_blog_post(duplicate_data)

    assert exc_info.value.field_name == 'title'
    assert exc_info.value.field_value == 'First Post'
    assert exc_info.value.message == "A blog post with this title already exists."


@pytest.mark.admin_upload_blog_posts
def test_save_blog_post_missing_fields(session) -> None:
    """Integration test for save_blog_post service with missing required fields.

    This test ensures that providing incomplete data raises a KeyError.
    """
    # Arrange: Create a dictionary with missing required fields
    incomplete_data = {
        'title': "Incomplete Post",
        'slug': "incomplete-post",
        'html_content': "<p>Content for the incomplete post.</p>",
        # Missing drive_file_id
    }

    # Act & Assert: Ensure that calling the service function raises a KeyError
    with pytest.raises(KeyError) as exc_info:
        save_blog_post(incomplete_data)

    # Assert: Check that the raised KeyError message mentions the missing key
    assert str(exc_info.value) == "'drive_file_id'", \
        "Expected KeyError for missing 'drive_file_id' field."


@pytest.mark.admin_upload_blog_posts
def test_save_blog_post_success(session) -> None:
    """Integration test for save_blog_post service with valid data.

    This test verifies that a valid blog post is saved correctly and returns
    the expected data as a BlogPost domain object.
    """
    # Arrange: Create a dictionary with valid blog post data
    valid_data = {
        'title': "First Post",
        'slug': "first-post",
        'html_content': "<p>Content for the first post.</p>",
        'drive_file_id': "unique_drive_file_id_1"
    }

    # Act: Save the blog post using the service function
    saved_post = save_blog_post(valid_data)

    # Assert: Validate that the saved post is a BlogPost domain object
    assert isinstance(saved_post, BlogPost)
    assert saved_post.title == valid_data['title']
    assert saved_post.slug == valid_data['slug']  # Check slug
    assert saved_post.html_content == valid_data['html_content']
    assert saved_post.drive_file_id == valid_data['drive_file_id']
