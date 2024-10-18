"""Unit tests for the read_file method of the GoogleDriveService class.

This module contains unit tests for the read_file method, which retrieves
the content of a specified file from Google Drive by file ID. The tests
verify that the method handles successful retrievals and errors appropriately.

Tests included:
    - test_read_file_success: Verifies that the method returns the file content
      for a valid file ID.
    - test_read_file_404_error: Verifies that a 404 HttpError raises
      GoogleDriveFileNotFoundError.
    - test_read_file_403_error: Verifies that a 403 HttpError raises
      GoogleDrivePermissionError.
    - test_read_file_other_http_error: Verifies that other HTTP errors raise
      GoogleDriveAPIError with an appropriate message.

Mocks:
    - Mocks are used to simulate the Google Drive API's files().export() method
      and its behavior in various scenarios, such as successful responses and errors.
"""

from unittest.mock import Mock

import pytest
from googleapiclient.errors import HttpError

from app.services import exceptions
from app.services.google_drive_service import GoogleDriveService


def test_read_file_success(mock_google_drive_service: GoogleDriveService) -> None:
    """Tests that a successful file read returns the file content."""
    # Arrange
    mock_google_drive_service.drive_service.files.return_value.export.return_value.execute \
        .return_value = (
            b'File content'
        )

    # Act
    result = mock_google_drive_service.read_file('file123')

    # Assert
    assert result == 'File content'
    mock_google_drive_service.drive_service.files.return_value.export.assert_called_once_with(
        fileId='file123',
        mimeType='text/plain'
    )


def test_read_file_404_error(mock_google_drive_service: GoogleDriveService) -> None:
    """Tests that a 404 HttpError raises GoogleDriveFileNotFoundError."""
    # Arrange
    mock_google_drive_service.drive_service.files.return_value.export.return_value \
        .execute.side_effect = HttpError(
            resp=Mock(status=404),
            content=b'File not found'
        )

    # Act & Assert
    with pytest.raises(
            exceptions.GoogleDriveFileNotFoundError,
            match="Resource not found during reading file."
    ):
        mock_google_drive_service.read_file('invalid_file')


def test_read_file_403_error(mock_google_drive_service: GoogleDriveService) -> None:
    """Tests that a 403 HttpError raises GoogleDrivePermissionError."""
    # Arrange
    mock_google_drive_service.drive_service.files.return_value.export.return_value \
        .execute.side_effect = HttpError(
            resp=Mock(status=403),
            content=b'Permission denied'
        )

    # Act & Assert
    with pytest.raises(
            exceptions.GoogleDrivePermissionError,
            match="Permission denied during reading file."
    ):
        mock_google_drive_service.read_file('restricted_file')


def test_read_file_other_http_error(mock_google_drive_service: GoogleDriveService) -> None:
    """Tests that other HttpErrors raise GoogleDriveAPIError."""
    # Arrange
    mock_error_content = b'{"error": {"message": "Server error"}}'
    mock_google_drive_service.drive_service.files.return_value.export.return_value \
        .execute.side_effect = HttpError(
            resp=Mock(status=500),
            content=mock_error_content
        )

    # Act & Assert
    with pytest.raises(
            exceptions.GoogleDriveAPIError,
            match="Google Drive API error occurred during reading file: Server error"
    ):
        mock_google_drive_service.read_file('file123')
