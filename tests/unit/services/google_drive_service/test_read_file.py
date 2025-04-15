"""Unit tests for the read_file method of the GoogleDriveService class.

This module contains unit tests for the `read_file` method of the
GoogleDriveService class, which retrieves the content of a specified file
from Google Drive by file ID. The tests verify that the method handles
successful operations and errors correctly, both in mocked and real API contexts.

Test Classes and Functions:

    TestReadFileMockedAPI:
        - test_read_file_403_error
        - test_read_file_404_error
        - test_read_file_other_http_error
        - test_read_file_success

    TestReadFileRealAPI:
        - test_read_file_not_found
        - test_read_file_permission_denied
        - test_read_file_success

Fixtures:
    - mock_google_drive_service: Mocks the Google Drive service interactions.
    - google_drive_service_fixture: Provides an instance of the real GoogleDriveService.
    - test_drive_file_metadata_map: Provides a mapping of human-readable aliases to real Google Drive file metadata
        for use in integration tests. Each entry is a dictionary containing 'file_id', 'slug', and 'title'.
"""

from unittest.mock import Mock

import pytest
from googleapiclient.errors import HttpError

from app import exceptions
from app.services.google_drive_service import GoogleDriveService


@pytest.mark.admin_upload_blog_posts
class TestReadFileMockedAPI:

    def test_read_file_403_error(self) -> None:
        """Tests that a 403 HttpError raises GoogleDrivePermissionError."""
        service = GoogleDriveService(drive_service=Mock())
        service.drive_service.files.return_value.export.return_value.execute.side_effect = HttpError(
            resp=Mock(status=403),
            content=b'Permission denied'
        )

        with pytest.raises(
                exceptions.GoogleDrivePermissionError,
                match="Permission denied during reading file."
        ):
            service.read_file('restricted_file')

    def test_read_file_404_error(self) -> None:
        """Tests that a 404 HttpError raises GoogleDriveFileNotFoundError."""
        service = GoogleDriveService(drive_service=Mock())
        service.drive_service.files.return_value.export.return_value.execute.side_effect = HttpError(
            resp=Mock(status=404),
            content=b'File not found'
        )

        with pytest.raises(
                exceptions.GoogleDriveFileNotFoundError,
                match="Resource not found during reading file."
        ):
            service.read_file('invalid_file')

    def test_read_file_other_http_error(self) -> None:
        """Tests that other HttpErrors raise GoogleDriveAPIError."""
        service = GoogleDriveService(drive_service=Mock())
        mock_error_content = b'{"error": {"message": "Server error"}}'
        service.drive_service.files.return_value.export.return_value.execute.side_effect = HttpError(
            resp=Mock(status=500),
            content=mock_error_content
        )

        with pytest.raises(
                exceptions.GoogleDriveAPIError,
                match="Google Drive API error occurred during reading file: Server error"
        ):
            service.read_file('file123')

    def test_read_file_success(self) -> None:
        """Tests that a successful file read returns the file content."""
        service = GoogleDriveService(drive_service=Mock())
        service.drive_service.files.return_value.export.return_value.execute.return_value = b'File content'

        result = service.read_file('file123')

        assert result == 'File content'
        service.drive_service.files.return_value.export.assert_called_once_with(
            fileId='file123',
            mimeType='text/plain'
        )


@pytest.mark.api
@pytest.mark.admin_upload_blog_posts
class TestReadFileRealAPI:

    def test_read_file_not_found(self, google_drive_service_fixture: GoogleDriveService) -> None:
        """Tests that reading a non-existent file raises an error."""
        with pytest.raises(exceptions.GoogleDriveFileNotFoundError) as exc_info:
            google_drive_service_fixture.read_file('non_existent_file_id')
        assert "Resource not found" in str(exc_info.value)

    def test_read_file_permission_denied(
            self,
            google_drive_service_fixture: GoogleDriveService,
            test_drive_file_metadata_map: dict
    ) -> None:
        """Tests that insufficient permissions raise a GoogleDriveFileNotFoundError.

        Google Drive API returns a 404 'File not found' error even when the file exists
        but is inaccessible due to insufficient permissions.
        """
        # Leverage the 'restricted' file metadata from the fixture
        restricted_file_metadata = test_drive_file_metadata_map["restricted"]
        file_id = restricted_file_metadata["file_id"]

        with pytest.raises(exceptions.GoogleDriveFileNotFoundError) as exc_info:
            google_drive_service_fixture.read_file(file_id)

        assert "Resource not found" in str(exc_info.value)

    def test_read_file_success(
            self,
            google_drive_service_fixture: GoogleDriveService,
            test_drive_file_metadata_map: dict
    ) -> None:
        """Tests reading the contents of a file with a valid file ID."""
        # Leverage the real_drive_file_metadata from the fixture
        file_metadata = test_drive_file_metadata_map["design_principles"]

        file_content = google_drive_service_fixture.read_file(file_metadata["file_id"])

        assert isinstance(file_content, str), "Expected file content to be a string."
        assert len(file_content) > 0, "File content should not be empty."

