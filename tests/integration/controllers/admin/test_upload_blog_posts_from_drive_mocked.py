"""Integration tests for the upload_blog_posts_from_drive controller function.

This module contains integration tests for the upload_blog_posts_from_drive
controller function, focusing on validating and sanitizing blog post data and
handling various scenarios, such as successful uploads, missing files, and runtime errors.

Tests included:
    - test_upload_blog_posts_from_drive_success: Verifies successful upload of blog posts.
    - test_upload_blog_posts_from_drive_no_files: Ensures validation errors when no files are
        provided.
    - test_upload_blog_posts_from_drive_missing_file_id: Verifies behavior when a file ID is
        missing.
    - test_upload_blog_posts_from_drive_file_not_found: Tests handling of a missing file error.
    - test_upload_blog_posts_from_drive_runtime_error: Tests handling of runtime errors during blog
        post saving.

Fixtures:
    - app: Provides the Flask application context for the tests.
    - session: Provides a session object for database interactions.
    - mocker: Provides mocking utilities for mocking external services.
"""

from unittest.mock import Mock

import pytest
from flask import Flask
from freezegun import freeze_time
from sqlalchemy.orm import Session

from app import exceptions
from app.controllers.admin_controller import upload_blog_posts_from_drive
from app.exceptions import GoogleDriveFileNotFoundError, GoogleDrivePermissionError


def test_upload_blog_posts_from_drive_no_files(app):
    """Test validation when no files are provided."""
    with app.app_context():
        # Act
        response, status_code = upload_blog_posts_from_drive([])

        # Assert
        assert status_code == 400
        assert response.json == {"error": "No files provided"}


def test_upload_blog_posts_from_drive_missing_file_id(app):
    """Test behavior when a file ID is missing in the payload."""
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


@pytest.mark.parametrize(
    "files, side_effects, expected_status, expected_response",
    [
        # Scenario 1: One success
        (
                [{"id": "valid_file_id", "title": "Valid Blog Post"}],
                ["Valid blog post content"],
                201,
                {
                    "success": [
                        {
                            "title": "Valid Blog Post",
                            "content": "<p>Valid blog post content</p>",
                            "drive_file_id": "valid_file_id",
                            "created_at": "2024-12-04T14:18:16+00:00",
                        }
                    ],
                    "errors": [],
                },
        ),
        # Scenario 2: Five successes
        (
                [{"id": f"valid_file_{i}_id", "title": f"Valid Blog Post {i}"} for i in range(5)],
                [f"Valid blog post content {i}" for i in range(5)],
                201,
                {
                    "success": [
                        {
                            "title": f"Valid Blog Post {i}",
                            "content": f"<p>Valid blog post content {i}</p>",
                            "drive_file_id": f"valid_file_{i}_id",
                            "created_at": "2024-12-04T14:18:16+00:00",
                        }
                        for i in range(5)
                    ],
                    "errors": [],
                },
        ),
    ],
)
@freeze_time("2024-12-04 14:18:16")
def test_upload_blog_posts_from_drive_success_only(
        app: Flask, mock_google_drive_service: Mock, session: Session, files, side_effects,
        expected_status, expected_response
) -> None:
    """Tests the behavior of uploading blog posts with only successful results.

    This test validates that:
    1. All valid files are successfully uploaded, with content sanitized and properly formatted.
    2. No errors occur during the upload process.
    3. The API returns a 200 status code indicating full success.
    4. The timestamps are correctly set and formatted (matching the frozen time).
    """
    with app.app_context():
        # Mock Google Drive service behavior
        mock_google_drive_service.read_file.side_effect = side_effects

        # Act
        response, status_code = upload_blog_posts_from_drive(files)

        # Assert
        assert status_code == expected_status
        assert response.get_json() == expected_response


def test_upload_blog_posts_from_drive_file_not_found(app, mock_google_drive_service):
    """Test handling of missing file errors."""
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


@pytest.mark.parametrize(
    "mock_google_drive_service, files, expected_status, expected_response",
    [
        # Scenario 1: 1 success, 1 failure
        (
                {"read_file_side_effect": ["Valid blog post content",
                                           GoogleDriveFileNotFoundError]},
                [
                    {"id": "valid_file_id", "title": "Valid Blog Post"},
                    {"id": "invalid_file_id", "title": "Invalid Blog Post"},
                ],
                207,
                {
                    "success": [
                        {
                            "title": "Valid Blog Post",
                            "content": "<p>Valid blog post content</p>",
                            "drive_file_id": "valid_file_id",
                            "created_at": "2024-12-04T14:18:16+00:00",
                        }
                    ],
                    "errors": [
                        {"file_id": "invalid_file_id", "error": "File not found on Google Drive"},
                    ],
                },
        ),
        # Scenario 2: 1 success, 3 failures
        (
                {
                    "read_file_side_effect": [
                        "Valid blog post content",
                        GoogleDriveFileNotFoundError,
                        exceptions.GoogleDrivePermissionError,
                        RuntimeError("Error saving blog post"),
                    ]
                },
                [
                    {"id": "valid_file_id", "title": "Valid Blog Post"},
                    {"id": "missing_file_id", "title": "Missing Blog Post"},
                    {"id": "permission_denied_file_id", "title": "Permission Denied Blog Post"},
                    {"id": "runtime_error_file_id", "title": "Runtime Error Blog Post"},
                ],
                207,
                {
                    "success": [
                        {
                            "title": "Valid Blog Post",
                            "content": "<p>Valid blog post content</p>",
                            "drive_file_id": "valid_file_id",
                            "created_at": "2024-12-04T14:18:16+00:00",
                        }
                    ],
                    "errors": [
                        {"file_id": "missing_file_id", "error": "File not found on Google Drive"},
                        {"file_id": "permission_denied_file_id", "error": "Permission denied"},
                        {"file_id": "runtime_error_file_id",
                         "error": "Error saving blog post: Error saving blog post"},
                    ],
                },
        ),
        # Scenario 3: 5 successes, 1 failure
        (
                {
                    "read_file_side_effect": [
                                                 f"Valid blog post content {i}" for i in range(5)
                                             ] + [GoogleDriveFileNotFoundError]
                },
                [
                    {"id": f"valid_file_{i}_id", "title": f"Valid Blog Post {i}"} for i in range(5)
                ] + [{"id": "invalid_file_id", "title": "Invalid Blog Post"}],
                207,
                {
                    "success": [
                        {
                            "title": f"Valid Blog Post {i}",
                            "content": f"<p>Valid blog post content {i}</p>",
                            "drive_file_id": f"valid_file_{i}_id",
                            "created_at": "2024-12-04T14:18:16+00:00",
                        }
                        for i in range(5)
                    ],
                    "errors": [
                        {"file_id": "invalid_file_id", "error": "File not found on Google Drive"},
                    ],
                },
        ),
    ],
    indirect=["mock_google_drive_service"],  # Indirectly parametrize the fixture
)
@freeze_time("2024-12-04 14:18:16")
def test_upload_blog_posts_from_drive_mixed_results(
        app: Flask, mock_google_drive_service: Mock, session: Session, files, expected_status,
        expected_response
) -> None:
    """Tests the behavior of uploading blog posts when both success and error cases occur.

    This test validates that:
    1. A valid file successfully uploads, with content sanitized and properly formatted.
    2. An invalid file triggers the correct error response.
    3. The API returns a 207 status code indicating mixed results.
    4. The timestamps are correctly set and formatted (matching the frozen time).
    """
    with app.app_context():
        # Act
        response, status_code = upload_blog_posts_from_drive(files)

        # Assert
        assert status_code == expected_status
        assert response.get_json() == expected_response


@pytest.mark.parametrize(
    "mock_google_drive_service",
    [{"save_blog_post_side_effect": RuntimeError("Simulated runtime error")}],
    indirect=True
)
def test_upload_blog_posts_from_drive_runtime_error(app, mock_google_drive_service, session):
    """Test handling of runtime errors during blog post saving when a single file fails."""
    # Arrange
    files = [{"id": "valid_id", "title": "valid_title"}]

    with app.app_context():
        # Act
        response, status_code = upload_blog_posts_from_drive(files=files)

    # Assert
    assert status_code == 400  # Expecting a 400 due to the runtime error
    assert response.get_json() == {
        "success": [],
        "errors": [
            {"file_id": "valid_id", "error": "Error saving blog post: Simulated runtime error"}]
    }


@pytest.mark.parametrize(
    "files, side_effects, expected_status, expected_response",
    [
        # Scenario 1: One error (File not found)
        (
                [{"id": "missing_file_id", "title": "Missing Blog Post"}],
                [GoogleDriveFileNotFoundError],
                400,
                {
                    "success": [],
                    "errors": [
                        {"file_id": "missing_file_id", "error": "File not found on Google Drive"}
                    ],
                },
        ),
        # Scenario 2: Three different errors
        (
                [
                    {"id": "missing_file_id", "title": "Missing Blog Post"},
                    {"id": "permission_denied_file_id", "title": "Permission Denied Blog Post"},
                    {"id": "runtime_error_file_id", "title": "Runtime Error Blog Post"},
                ],
                [
                    GoogleDriveFileNotFoundError,
                    GoogleDrivePermissionError,
                    RuntimeError("Error saving blog post"),
                ],
                400,
                {
                    "success": [],
                    "errors": [
                        {"file_id": "missing_file_id", "error": "File not found on Google Drive"},
                        {"file_id": "permission_denied_file_id", "error": "Permission denied"},
                        {"file_id": "runtime_error_file_id",
                         "error": "Error saving blog post: Error saving blog post"},
                    ],
                },
        ),
        # Scenario 3: Five same kind of errors (File not found)
        (
                [{"id": f"missing_file_{i}_id", "title": f"Missing Blog Post {i}"} for i in
                 range(5)],
                [GoogleDriveFileNotFoundError] * 5,
                400,
                {
                    "success": [],
                    "errors": [
                        {"file_id": f"missing_file_{i}_id",
                         "error": "File not found on Google Drive"}
                        for i in range(5)
                    ],
                },
        ),
    ],
)
@freeze_time("2024-12-04 14:18:16")
def test_upload_blog_posts_from_drive_errors_only(
        app: Flask, mock_google_drive_service: Mock, session: Session, files, side_effects,
        expected_status, expected_response
) -> None:
    """Tests the behavior of uploading blog posts with only errors occurring.

    This test validates that:
    1. No files are successfully uploaded due to errors.
    2. Appropriate error messages are returned for each failed file.
    3. The API returns a 207 status code indicating mixed results, despite all failures.
    4. The error handling matches the raised exceptions and files.
    """
    with app.app_context():
        # Mock Google Drive service behavior
        mock_google_drive_service.read_file.side_effect = side_effects

        # Act
        response, status_code = upload_blog_posts_from_drive(files)

        # Assert
        assert status_code == expected_status
        assert response.get_json() == expected_response


@pytest.mark.parametrize(
    "files, side_effects, expected_status, expected_response",
    [
        # Scenario 1: Single file, unexpected error, immediate halt
        (
            [{"id": "unexpected_error_file_id", "title": "Unexpected Error Blog Post"}],
            [Exception("Unexpected error occurred")],
            500,
            {
                "success": [],
                "errors": [
                    {
                        "file_id": "unexpected_error_file_id",
                        "error": "Unexpected error occurred.",
                    }
                ],
            },
        ),
        # Scenario 2: Expected error, then unexpected error, immediate halt
        (
            [
                {"id": "expected_error_file_id", "title": "Expected Error Blog Post"},
                {"id": "unexpected_error_file_id", "title": "Unexpected Error Blog Post"},
            ],
            [
                ValueError("File not found"),
                Exception("Unexpected error occurred"),
            ],
            500,
            {
                "success": [],
                "errors": [
                    {
                        "file_id": "expected_error_file_id",
                        "error": "File not found",
                    },
                    {
                        "file_id": "unexpected_error_file_id",
                        "error": "Unexpected error occurred.",
                    },
                ],
            },
        ),
        # Scenario 3: One success, then unexpected error, immediate halt
        (
            [
                {"id": "success_file_id", "title": "Successful Blog Post"},
                {"id": "unexpected_error_file_id", "title": "Unexpected Error Blog Post"},
            ],
            [
                {"file_id": "success_file_id", "message": "Processed successfully"},
                Exception("Unexpected error occurred"),
            ],
            500,
            {
                "success": [
                    {"file_id": "success_file_id", "message": "Processed successfully"}
                ],
                "errors": [
                    {
                        "file_id": "unexpected_error_file_id",
                        "error": "Unexpected error occurred",
                    },
                ],
            },
        ),
        # Scenario 4: Three successes, then critical error, immediate halt
        (
            [
                {"id": "success_file_id_1", "title": "Successful Blog Post 1"},
                {"id": "success_file_id_2", "title": "Successful Blog Post 2"},
                {"id": "success_file_id_3", "title": "Successful Blog Post 3"},
                {"id": "critical_error_file_id", "title": "Critical Error Blog Post"},
                {"id": "unprocessed_file_id", "title": "Unprocessed Blog Post"},
            ],
            [
                {"file_id": "success_file_id_1", "message": "Processed successfully"},
                {"file_id": "success_file_id_2", "message": "Processed successfully"},
                {"file_id": "success_file_id_3", "message": "Processed successfully"},
                Exception("Critical error occurred"),
            ],
            500,
            {
                "success": [
                    {"file_id": "success_file_id_1", "message": "Processed successfully"},
                    {"file_id": "success_file_id_2", "message": "Processed successfully"},
                    {"file_id": "success_file_id_3", "message": "Processed successfully"},
                ],
                "errors": [
                    {
                        "file_id": "critical_error_file_id",
                        "error": "Critical error occurred",
                    },
                ],
            },
        ),
    ],
)
@freeze_time("2024-12-04 14:18:16")
def test_upload_blog_posts_from_drive_unexpected_error(
    app: Flask, mock_google_drive_service: Mock, session: Session, files, side_effects,
    expected_status, expected_response
) -> None:
    """Tests the behavior of uploading blog posts when a critical error happens."""
    with app.app_context():
        # Arrange
        mock_google_drive_service.read_file.side_effect = side_effects

        # Act
        response, status_code = upload_blog_posts_from_drive(files)

        # Assert
        assert status_code == expected_status, f"Expected {expected_status}, got {status_code}"
        assert response == expected_response, (
            f"Expected response: {expected_response}, got {response}"
        )

