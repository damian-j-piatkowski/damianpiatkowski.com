"""Integration tests for the upload_blog_posts_from_drive controller function.

This module contains tests for the `upload_blog_posts_from_drive` function,
which is responsible for uploading blog posts from Google Drive to the database.
The tests verify the function's behavior under various scenarios, including successful
uploads, validation errors, and unexpected issues.

Tests included:
    - test_upload_blog_posts_from_drive_errors_only: Verifies that only error cases are
      handled properly, returning the expected error responses.
    - test_upload_blog_posts_from_drive_file_not_found: Verifies that a missing file in
      Google Drive triggers the appropriate error handling.
    - test_upload_blog_posts_from_drive_missing_file_id: Verifies behavior when the payload
      lacks required fields like the file ID.
    - test_upload_blog_posts_from_drive_mixed_results: Verifies that mixed cases (success
      and error) are handled correctly, with proper status codes and responses.
    - test_upload_blog_posts_from_drive_no_files: Verifies that the function validates
      input and rejects empty file lists.
    - test_upload_blog_posts_from_drive_success_only: Verifies successful uploads of all
      valid files, ensuring database integrity and response correctness.
    - test_upload_blog_posts_from_drive_unexpected_error: Verifies handling of unexpected
      errors during the upload process.
    - test_upload_blog_posts_from_drive_with_actual_api: Verifies uploading blog posts
      using the real Google Drive API, including database persistence and response validation.

Fixtures:
    - app: Provides the Flask application context for testing.
    - mock_google_drive_service: Mocks the Google Drive service interactions.
    - session: Manages the database session for test data verification.
"""

from typing import Dict, Any
from unittest.mock import Mock

import pytest
from flask import Flask
from freezegun import freeze_time
from sqlalchemy.orm import Session

from app import exceptions
from app.controllers.admin_controller import upload_blog_posts_from_drive
from tests.scenarios.upload_blog_posts import (
    errors_only, unexpected_error_included, mixed_results, successful_only
)


@pytest.mark.parametrize("scenario", errors_only.scenarios)
@freeze_time("2024-12-04 14:18:16")
def test_upload_blog_posts_from_drive_errors_only(
        app: Flask,
        mock_google_drive_service: Mock,
        session: Session,
        scenario: Dict[str, Any]
) -> None:
    """Tests the behavior of uploading blog posts with only errors occurring."""
    with app.app_context():
        # Arrange
        mock_google_drive_service.read_file.side_effect = scenario["side_effects"]

        # Act
        response, status_code = upload_blog_posts_from_drive(scenario["files"])

        # Assert
        assert status_code == scenario["expected_status"]
        assert response == scenario["expected_response"]


def test_upload_blog_posts_from_drive_file_not_found(app, mock_google_drive_service):
    """Tests handling of missing file errors."""
    # Arrange
    files = [{"id": "non_existent_id", "title": "Non-existent Post"}]

    # Configure the mock to raise the file-not-found error for the specified file
    mock_google_drive_service.read_file.side_effect = exceptions.GoogleDriveFileNotFoundError

    with app.app_context():
        # Act
        response, status_code = upload_blog_posts_from_drive(files=files)

    # Assert
    assert status_code == 400  # Bad Request for no valid files
    assert response.get_json() == {
        "success": [],
        "errors": [
            {"file_id": "non_existent_id", "error": "File not found on Google Drive"}
        ],
    }


def test_upload_blog_posts_from_drive_missing_file_id(app):
    """Tests behavior when a file ID is missing in the payload."""
    with app.app_context():
        # Arrange
        files = [{"title": "missing_id"}]  # Payload missing "id"

        # Act
        response, status_code = upload_blog_posts_from_drive(files)

        # Assert
        assert status_code == 400  # Bad Request since the payload is invalid
        assert response.get_json() == {
            "success": [],
            "errors": [{"file": {"title": "missing_id"}, "error": "Missing required fields"}],
        }


@pytest.mark.parametrize("scenario", mixed_results.scenarios)
@freeze_time("2024-12-04 14:18:16")
def test_upload_blog_posts_from_drive_mixed_results(
        app: Flask,
        mock_google_drive_service: Mock,
        session: Session,
        scenario: Dict[str, Any]
) -> None:
    """Tests the behavior of uploading blog posts when both success and error cases occur."""
    with app.app_context():
        # Arrange
        mock_google_drive_service.read_file.side_effect = scenario["side_effects"]

        # Act
        response, status_code = upload_blog_posts_from_drive(scenario["files"])

        # Assert
        assert status_code == scenario["expected_status"]
        assert response == scenario["expected_response"]


def test_upload_blog_posts_from_drive_no_files(app):
    """Tests validation when no files are provided."""
    with app.app_context():
        # Act
        response, status_code = upload_blog_posts_from_drive([])

        # Assert
        assert status_code == 400
        assert response.json == {"error": "No files provided"}


@pytest.mark.parametrize("scenario", successful_only.scenarios)
@freeze_time("2024-12-04 14:18:16")
def test_upload_blog_posts_from_drive_success_only(
        app: Flask,
        mock_google_drive_service: Mock,
        session: Session,
        scenario: Dict[str, Any]
) -> None:
    """Tests the behavior of uploading blog posts with only successful results."""
    with app.app_context():
        # Arrange
        mock_google_drive_service.read_file.side_effect = scenario["side_effects"]

        # Act
        response, status_code = upload_blog_posts_from_drive(scenario["files"])

        # Assert
        assert status_code == scenario["expected_status"]
        assert response == scenario["expected_response"]


@pytest.mark.parametrize("scenario", unexpected_error_included.scenarios)
@freeze_time("2024-12-04 14:18:16")
def test_upload_blog_posts_from_drive_unexpected_error(
        app: Flask,
        mock_google_drive_service: Mock,
        session: Session,
        scenario: Dict[str, Any]
) -> None:
    """Tests handling of unexpected errors during the upload of blog posts from Google Drive."""
    with app.app_context():
        # Arrange
        mock_google_drive_service.read_file.side_effect = scenario["side_effects"]

        # Act
        response, status_code = upload_blog_posts_from_drive(scenario["files"])

        # Assert
        assert status_code == scenario["expected_status"]
        assert response == scenario["expected_response"]


@pytest.mark.api
def test_upload_blog_posts_from_drive_with_actual_api(app, google_drive_service_fixture, session):
    """Tests uploading blog posts using the actual Google Drive API."""
    with app.app_context():
        files = [
            {
                "id": "1p5jpGiSa1KyXbQrAEJ44NEBP4pgsLqpsdgYUkMgy3Vo",
                "title": "six_essential_object_oriented_design_principles_from_matthias_"
                         "nobacks_object_design_style_guide"
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
            assert saved_post is not None, (f"Blog post for file ID {file_id} was not found "
                                            f"in the database.")
            assert saved_post.title == file_title, f"Database title mismatch for file ID {file_id}."
            assert len(
                saved_post.content) > 0, (f"Database content should not be empty "
                                          f"for file ID {file_id}.")
