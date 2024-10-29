"""Integration tests for the upload_blog_post controller function.

This module contains integration tests for the upload_blog_post function,
focusing on validating and sanitizing blog post data and handling various
scenarios, such as successful uploads, validation errors, and runtime errors.

Tests included:
    - test_upload_blog_post_runtime_error: Tests handling of a runtime error during blog post saving.
    - test_upload_blog_post_success: Verifies successful upload of a blog post.
    - test_upload_blog_post_validation_error: Ensures validation errors are handled when data is invalid.

Fixtures:
    - app: Provides the Flask application context for the tests.
    - session: Provides a session object for database interactions.
"""

from app.controllers.admin_controller import upload_blog_post


def test_upload_blog_post_runtime_error(app, session, mocker) -> None:
    """Test handling of a runtime error during blog post saving."""
    with app.app_context():
        # Mock save_blog_post to raise a RuntimeError
        mocker.patch('app.services.blog_service.save_blog_post',
                     side_effect=RuntimeError("Database error"))

        # Prepare test data
        data = {"title": "Test Post", "content": "Sample content"}

        # Call the function and assert response and status code
        response, status_code = upload_blog_post(data)
        assert status_code == 500
        assert response.json == {'error': 'Database error'}


def test_upload_blog_post_success(app, session) -> None:
    """Verifies successful upload of a blog post."""
    with app.app_context():
        # Prepare test data
        data = {"title": "Test Post", "content": "Sample content"}

        # Call the function and assert response and status code
        response, status_code = upload_blog_post(data)
        assert status_code == 201
        assert response.json == data


def test_upload_blog_post_validation_error(app, session) -> None:
    """Ensures validation errors are handled when data is invalid."""
    with app.app_context():
        # Prepare invalid test data (missing required title field)
        data = {"content": "Sample content without title"}

        # Call the function and assert response and status code
        response, status_code = upload_blog_post(data)
        assert status_code == 400
        assert 'title' in response.json
