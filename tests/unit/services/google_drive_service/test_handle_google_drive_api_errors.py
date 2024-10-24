"""Unit tests for the _handle_google_drive_api_errors method of the GoogleDriveService class.

This module contains unit tests for the _handle_google_drive_api_errors method, which
ensures that different types of Google Drive API errors are handled appropriately and
custom exceptions are raised when needed. The method can handle specific HTTP errors
as well as unexpected exceptions.

Tests included:
    - test_handle_google_drive_api_errors_404: Verifies that a 404 status raises
      GoogleDriveFileNotFoundError.
    - test_handle_google_drive_api_errors_403: Verifies that a 403 status raises
      GoogleDrivePermissionError.
    - test_handle_google_drive_api_errors_other_error: Verifies that other HTTP errors
      raise GoogleDriveAPIError with appropriate messages.
    - test_handle_google_drive_api_errors_unexpected_error: Verifies that unexpected
      non-HTTP exceptions also raise GoogleDriveAPIError.

Mocks:
    - Mock objects are used to simulate HTTP responses for various status codes and
      error content.
"""

import json
from unittest.mock import Mock

import pytest
from googleapiclient.errors import HttpError

from app import exceptions
from app.services.google_drive_service import GoogleDriveService


def test_handle_google_drive_api_errors_404() -> None:
    """Tests that a 404 HttpError raises GoogleDriveFileNotFoundError."""
    # Arrange
    mock_resp = Mock(status=404)
    error = HttpError(mock_resp, b'File not found')

    # Act & Assert
    with pytest.raises(
            exceptions.GoogleDriveFileNotFoundError,
            match="Resource not found during operation."
    ):
        GoogleDriveService._handle_google_drive_api_errors(error)


def test_handle_google_drive_api_errors_403() -> None:
    """Tests that a 403 HttpError raises GoogleDrivePermissionError."""
    # Arrange
    mock_resp = Mock(status=403)
    error = HttpError(mock_resp, b'Permission denied')

    # Act & Assert
    with pytest.raises(
            exceptions.GoogleDrivePermissionError,
            match="Permission denied during operation."
    ):
        GoogleDriveService._handle_google_drive_api_errors(error)


def test_handle_google_drive_api_errors_other_error() -> None:
    """Tests that other HttpErrors raise GoogleDriveAPIError."""
    # Arrange
    mock_resp = Mock(status=500)
    error_content = json.dumps({"error": {"message": "Server error"}}).encode("utf-8")
    error = HttpError(mock_resp, error_content)

    # Act & Assert
    with pytest.raises(
            exceptions.GoogleDriveAPIError,
            match="Google Drive API error occurred during operation: Server error"
    ):
        GoogleDriveService._handle_google_drive_api_errors(error)


def test_handle_google_drive_api_errors_unexpected_error() -> None:
    """Tests that non-HttpError exceptions raise GoogleDriveAPIError."""
    # Arrange
    error = Exception("Unexpected error")

    # Act & Assert
    with pytest.raises(
            exceptions.GoogleDriveAPIError,
            match="Unexpected error occurred during operation: Unexpected error"
    ):
        GoogleDriveService._handle_google_drive_api_errors(error)