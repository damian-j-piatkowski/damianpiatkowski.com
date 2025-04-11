"""Unit tests for the list_folder_contents method of the GoogleDriveService class.

This module contains unit tests for the `list_folder_contents` method of the
GoogleDriveService class, which retrieves the contents of a folder on Google Drive
by folder ID. The tests verify that the method handles successful operations and
error conditions correctly.

Test Classes and Functions:

    TestListFolderContentsMockedAPI:
        - test_list_folder_contents_403_error
        - test_list_folder_contents_404_error
        - test_list_folder_contents_empty_folder
        - test_list_folder_contents_other_http_error
        - test_list_folder_contents_success

    TestListFolderContentsRealAPI:
        - test_list_folder_contents_not_found
        - test_list_folder_contents_success

Fixtures:
    - mock_google_drive_service: Mocks the Google Drive service interactions.
    - google_drive_service_fixture: Provides an instance of the real GoogleDriveService.
    - real_folder_id: Provides a valid folder ID from the app configuration.
"""

import re
from unittest.mock import Mock

import pytest
from googleapiclient.errors import HttpError

from app import exceptions
from app.exceptions import GoogleDrivePermissionError
from app.services.google_drive_service import GoogleDriveService


class TestListFolderContentsMockedAPI:

    def test_list_folder_contents_403_error(self, mocker):
        """Tests that a 403 HttpError raises GoogleDrivePermissionError."""
        # Create a real instance of the service
        service = GoogleDriveService(drive_service=Mock())

        # Mock the drive_service behavior to raise a 403 error
        service.drive_service.files.return_value.list.return_value.execute.side_effect = HttpError(
            resp=Mock(status=403), content=b'Permission denied'
        )

        # Run the test
        with pytest.raises(GoogleDrivePermissionError):
            service.list_folder_contents("some-folder-id")

    def test_list_folder_contents_404_error(self):
        """Tests that a 404 HttpError raises GoogleDriveFileNotFoundError."""
        service = GoogleDriveService(drive_service=Mock())
        service.drive_service.files.return_value.list.return_value.execute.side_effect = HttpError(
            resp=Mock(status=404), content=b'Folder not found'
        )

        with pytest.raises(
                exceptions.GoogleDriveFileNotFoundError,
                match="Resource not found during listing folder contents."
        ):
            service.list_folder_contents('invalid_folder')

    def test_list_folder_contents_empty_folder(self):
        """Tests that an empty folder returns an empty list."""
        service = GoogleDriveService(drive_service=Mock())
        mock_list = service.drive_service.files.return_value.list
        mock_list.return_value.execute.return_value = {'files': []}

        result = service.list_folder_contents('empty_folder')

        assert result == []
        mock_list.assert_called_once_with(
            q="'empty_folder' in parents and trashed = false",
            fields="files(id, name)"
        )

    def test_list_folder_contents_other_http_error(self):
        """Tests that other HttpErrors raise GoogleDriveAPIError."""
        service = GoogleDriveService(drive_service=Mock())
        mock_error_content = b'{"error": {"message": "Server error"}}'
        service.drive_service.files.return_value.list.return_value.execute.side_effect = HttpError(
            resp=Mock(status=500), content=mock_error_content
        )

        with pytest.raises(
                exceptions.GoogleDriveAPIError,
                match="Google Drive API error occurred during listing folder contents: Server error"
        ):
            service.list_folder_contents('folder123')

    def test_list_folder_contents_success(self):
        """Tests that a successful folder listing returns the expected files."""
        service = GoogleDriveService(drive_service=Mock())
        mock_response = {
            'files': [{'id': 'file1', 'name': 'File 1'}, {'id': 'file2', 'name': 'File 2'}]
        }
        mock_list = service.drive_service.files.return_value.list
        mock_list.return_value.execute.return_value = mock_response

        result = service.list_folder_contents('folder123')

        assert result == mock_response['files']
        mock_list.assert_called_once_with(
            q="'folder123' in parents and trashed = false",
            fields="files(id, name)"
        )


@pytest.mark.api
class TestListFolderContentsRealAPI:

    def test_list_folder_contents_not_found(self, google_drive_service_fixture: GoogleDriveService) -> None:
        """Tests that listing contents of a non-existent folder raises an error."""
        with pytest.raises(exceptions.GoogleDriveFileNotFoundError) as exc_info:
            google_drive_service_fixture.list_folder_contents('non_existent_folder_id')

        assert "Resource not found during listing folder contents" in str(exc_info.value)

    def test_list_folder_contents_success(
            self,
            google_drive_service_fixture: GoogleDriveService,
            real_folder_id: str
    ) -> None:
        """Tests listing contents of a valid folder ID (real API call)."""
        folder_contents = google_drive_service_fixture.list_folder_contents(real_folder_id)

        # Structural assertions
        assert isinstance(folder_contents, list), "Expected folder contents to be a list."
        assert all('id' in file and 'name' in file for file in folder_contents), \
            "Each file should contain an 'id' and 'name'."
        assert folder_contents, "Folder should contain at least one file."

        # Format assertion: all names should follow kebab-case with numeric prefix
        filename_pattern = re.compile(r'^\d{2}-[a-z0-9]+(-[a-z0-9]+)*$')
        for file in folder_contents:
            assert filename_pattern.match(file['name']), f"File name format invalid: {file['name']}"

        # Known good file presence
        expected_name = (
            "01-six-essential-object-oriented-design-principles-from-"
            "matthias-nobacks-object-design-style-guide"
        )
        assert any(file['name'] == expected_name for file in folder_contents), \
            f"Expected file name '{expected_name}' not found in folder contents."

        # Restricted file should not be listed
        restricted_file = "00-test-restricted-access"
        assert all(file['name'] != restricted_file for file in folder_contents), \
            f"Restricted file '{restricted_file}' should not be accessible or listed."
