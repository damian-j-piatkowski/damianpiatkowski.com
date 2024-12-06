"""Integration tests for the upload_blog_posts_from_drive controller function.

This module contains integration tests for the upload_blog_posts_from_drive
controller function, focusing on validating and sanitizing blog post data and
handling various scenarios, such as successful uploads, missing files, and runtime errors.

Tests included:
    - test_upload_blog_posts_from_drive_success: Verifies successful upload of blog posts.
    - test_upload_blog_posts_from_drive_no_files: Ensures validation errors when no files are provided.
    - test_upload_blog_posts_from_drive_missing_file_id: Verifies behavior when a file ID is missing.
    - test_upload_blog_posts_from_drive_file_not_found: Tests handling of a missing file error.
    - test_upload_blog_posts_from_drive_runtime_error: Tests handling of runtime errors during blog post saving.

Fixtures:
    - app: Provides the Flask application context for the tests.
    - session: Provides a session object for database interactions.
    - mocker: Provides mocking utilities for mocking external services.
"""

from app import exceptions
import pytest
from app.controllers.admin_controller import upload_blog_posts_from_drive

@pytest.mark.api
def test_upload_blog_posts_from_drive_with_actual_api(app, google_drive_service_fixture, session):
    """Test uploading blog posts using the actual Google Drive API."""
    with app.app_context():
        files = [
            {
                "id": "1p5jpGiSa1KyXbQrAEJ44NEBP4pgsLqpsdgYUkMgy3Vo",
                "title": "six_essential_object_oriented_design_principles_from_matthias_nobacks_object_design_style_guide"
                # noqa: E501
            }
        ]

        # Act: Call the controller function directly with the test files
        response_data, status_code = upload_blog_posts_from_drive(files)

        # Assert: Verify the status code and response data
        assert status_code == 201
        assert len(response_data) == len(files)

        for file in files:
            file_id = file["id"]
            file_title = file["title"]

            # Check that the response matches the expected data
            uploaded_post = next(
                (post for post in response_data if post["drive_file_id"] == file_id), None
            )
            assert uploaded_post is not None, f"Blog post for file ID {file_id} was not created."
            assert uploaded_post["title"] == file_title, "Title mismatch in uploaded post."
            assert "content" in uploaded_post and len(
                uploaded_post["content"]) > 0, "Content should not be empty."

            # Query the database to verify the post was saved
            from app.models.tables.blog_post import blog_posts

            saved_post = session.query(blog_posts).filter_by(drive_file_id=file_id).one_or_none()
            assert saved_post is not None, f"Blog post for file ID {file_id} was not found in the database."
            assert saved_post.title == file_title, f"Database title mismatch for file ID {file_id}."
            assert len(
                saved_post.content) > 0, f"Database content should not be empty for file ID {file_id}."