"""Unit tests for the list_folder_contents method of the GoogleDriveService class.

This module contains unit tests for the list_folder_contents method, which retrieves
the contents of a specified folder from Google Drive. The tests verify that the
method handles successful retrievals and errors appropriately.

Tests included:
    - test_list_folder_contents_success: Verifies that the method returns a list of
      files with correct IDs and names.
    - test_list_folder_contents_empty_folder: Verifies that an empty folder returns
      an empty list.
    - test_list_folder_contents_404_error: Verifies that a 404 HttpError raises
      GoogleDriveFileNotFoundError.
    - test_list_folder_contents_403_error: Verifies that a 403 HttpError raises
      GoogleDrivePermissionError.
    - test_list_folder_contents_other_http_error: Verifies that other HTTP errors
      raise GoogleDriveAPIError with an appropriate message.

Mocks:
    - Mocks are used to simulate the Google Drive API's files().list() method and
      its behavior in various scenarios, such as successful responses and errors.
"""

from unittest.mock import Mock

import pytest
from googleapiclient.errors import HttpError

from app.services import exceptions
from app.services.google_drive_service import GoogleDriveService


def test_list_folder_contents_success(mock_google_drive_service: GoogleDriveService) -> None:
    """Tests that a successful folder listing returns the expected files."""
    # Arrange
    mock_response = {
        'files': [{'id': 'file1', 'name': 'File 1'}, {'id': 'file2', 'name': 'File 2'}]
    }

    # Mock the chained method files().list().execute()
    mock_list = mock_google_drive_service.drive_service.files.return_value.list
    mock_list.return_value.execute.return_value = mock_response

    # Act
    result = mock_google_drive_service.list_folder_contents('folder123')

    # Assert
    assert result == mock_response['files']
    mock_list.assert_called_once_with(
        q="'folder123' in parents and trashed = false",
        fields="files(id, name)"
    )


def test_list_folder_contents_empty_folder(mock_google_drive_service: GoogleDriveService) -> None:
    """Tests that an empty folder returns an empty list."""
    # Arrange
    mock_list = mock_google_drive_service.drive_service.files.return_value.list
    mock_list.return_value.execute.return_value = {'files': []}

    # Act
    result = mock_google_drive_service.list_folder_contents('empty_folder')

    # Assert
    assert result == []
    mock_list.assert_called_once_with(
        q="'empty_folder' in parents and trashed = false",
        fields="files(id, name)"
    )


def test_list_folder_contents_404_error(mock_google_drive_service: GoogleDriveService) -> None:
    """Tests that a 404 HttpError raises GoogleDriveFileNotFoundError."""
    # Arrange
    mock_google_drive_service.drive_service.files().list().execute.side_effect = HttpError(
        resp=Mock(status=404), content=b'Folder not found'
    )

    # Act & Assert
    with pytest.raises(exceptions.GoogleDriveFileNotFoundError,
                       match="Resource not found during listing folder contents."):
        mock_google_drive_service.list_folder_contents('invalid_folder')


def test_list_folder_contents_403_error(mock_google_drive_service: GoogleDriveService) -> None:
    """Tests that a 403 HttpError raises GoogleDrivePermissionError."""
    # Arrange
    mock_google_drive_service.drive_service.files().list().execute.side_effect = HttpError(
        resp=Mock(status=403), content=b'Permission denied'
    )

    # Act & Assert
    with pytest.raises(exceptions.GoogleDrivePermissionError,
                       match="Permission denied during listing folder contents."):
        mock_google_drive_service.list_folder_contents('restricted_folder')


def test_list_folder_contents_other_http_error(
        mock_google_drive_service: GoogleDriveService) -> None:
    """Tests that other HttpErrors raise GoogleDriveAPIError."""
    # Arrange
    mock_error_content = b'{"error": {"message": "Server error"}}'
    mock_google_drive_service.drive_service.files().list().execute.side_effect = HttpError(
        resp=Mock(status=500), content=mock_error_content
    )

    # Act & Assert
    with pytest.raises(
            exceptions.GoogleDriveAPIError,
            match="Google Drive API error occurred during listing folder contents: Server error"
    ):
        mock_google_drive_service.list_folder_contents('folder123')
