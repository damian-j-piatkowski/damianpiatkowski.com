"""Unit tests for the list_folder_contents method of the GoogleDriveService class.

This module contains unit tests for the `list_folder_contents` method of the
GoogleDriveService class, which retrieves the contents of a folder on Google Drive
by folder ID. The tests verify that the method handles successful operations and
error conditions correctly.
"""

import re
from unittest.mock import Mock

import pytest
from googleapiclient.errors import HttpError

from app import exceptions
from app.exceptions import GoogleDrivePermissionError
from app.services.google_drive_service import GoogleDriveService


@pytest.mark.admin_unpublished_posts
class TestListFolderContentsMockedAPI:
    """Unit tests for list_folder_contents() using a mocked Google Drive service."""

    def test_list_folder_contents_403_error(self):
        """403 error should raise GoogleDrivePermissionError."""
        service = GoogleDriveService(drive_service=Mock())
        service.drive_service.files.return_value.list.return_value.execute.side_effect = HttpError(
            resp=Mock(status=403), content=b'{"error": {"message": "Access denied"}}'
        )

        # Updated regex to match the final raised message
        with pytest.raises(GoogleDrivePermissionError, match=r"Permission denied.*listing folder contents"):
            service.list_folder_contents("some-folder-id")

    def test_list_folder_contents_404_error(self):
        """404 error should raise GoogleDriveFileNotFoundError."""
        service = GoogleDriveService(drive_service=Mock())
        service.drive_service.files.return_value.list.return_value.execute.side_effect = HttpError(
            resp=Mock(status=404), content=b'{"error": {"message": "Folder not found"}}'
        )

        # Updated regex to match the final raised message
        with pytest.raises(
                exceptions.GoogleDriveFileNotFoundError,
                match=r"Resource not found.*listing folder contents"
        ):
            service.list_folder_contents('invalid_folder')

    def test_list_folder_contents_empty_folder(self):
        """Empty folder should return empty list."""
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
        """Any other HTTP error should raise GoogleDriveAPIError with extracted message."""
        service = GoogleDriveService(drive_service=Mock())
        service.drive_service.files.return_value.list.return_value.execute.side_effect = HttpError(
            resp=Mock(status=500),
            content=b'{"error": {"message": "Internal Server Error"}}'
        )

        with pytest.raises(
            exceptions.GoogleDriveAPIError,
            match="Internal Server Error"
        ):
            service.list_folder_contents('folder123')

    def test_list_folder_contents_success(self):
        """Success case should return file list."""
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


@pytest.mark.admin_unpublished_posts
@pytest.mark.api
class TestListFolderContentsRealAPI:
    """Integration-style tests for list_folder_contents() using real API access."""

    def test_list_folder_contents_not_found(self, google_drive_service_fixture: GoogleDriveService) -> None:
        """Non-existent folder should raise GoogleDriveFileNotFoundError."""
        with pytest.raises(exceptions.GoogleDriveFileNotFoundError) as exc_info:
            google_drive_service_fixture.list_folder_contents('non_existent_folder_id')

        assert "Resource not found" in str(exc_info.value)

    def test_list_folder_contents_success(
        self,
        google_drive_service_fixture: GoogleDriveService,
        real_folder_id: str
    ) -> None:
        """Success path should list files with correct naming pattern and exclusions."""
        folder_contents = google_drive_service_fixture.list_folder_contents(real_folder_id)

        assert isinstance(folder_contents, list), "Expected a list of files."
        assert all('id' in file and 'name' in file for file in folder_contents), \
            "Each file must contain 'id' and 'name'."
        assert folder_contents, "Folder should not be empty."

        # Validate naming format
        filename_pattern = re.compile(r'^\d{2}-[a-z0-9]+(-[a-z0-9]+)*$')
        for file in folder_contents:
            assert filename_pattern.match(file['name']), f"Invalid file name: {file['name']}"

        expected_name = (
            "01-six-essential-object-oriented-design-principles-from-"
            "matthias-nobacks-object-design-style-guide"
        )
        assert any(file['name'] == expected_name for file in folder_contents), \
            f"Expected file '{expected_name}' not found."

        restricted_file = "00-test-restricted-access"
        assert all(file['name'] != restricted_file for file in folder_contents), \
            f"Restricted file '{restricted_file}' should not be listed."
