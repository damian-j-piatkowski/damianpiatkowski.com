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
    - google_drive_service_fixture: Real GoogleDriveService instance with credentials.
    - test_drive_file_metadata_map: Mapping of test file metadata including ID, slug, and title.
"""

from unittest.mock import Mock

import pytest
from googleapiclient.errors import HttpError

from app import exceptions
from app.services.google_drive_service import GoogleDriveService


@pytest.mark.admin_upload_blog_posts
class TestReadFileMockedAPI:
    """Unit tests for read_file() using a mocked Google Drive API."""

    def test_read_file_403_error(self) -> None:
        """Raises GoogleDrivePermissionError on a 403 error."""
        mock_execute = Mock()
        mock_execute.execute.side_effect = HttpError(resp=Mock(status=403), content=b'Permission denied')
        mock_export = Mock(return_value=mock_execute)
        mock_files = Mock()
        mock_files.export = mock_export
        mock_drive_service = Mock()
        mock_drive_service.files.return_value = mock_files
        service = GoogleDriveService(drive_service=mock_drive_service)

        with pytest.raises(exceptions.GoogleDrivePermissionError, match="Permission denied during reading file."):
            service.read_file('restricted_file')

    def test_read_file_404_error(self) -> None:
        """Raises GoogleDriveFileNotFoundError on a 404 error."""
        mock_execute = Mock()
        mock_execute.execute.side_effect = HttpError(resp=Mock(status=404), content=b'File not found')
        mock_export = Mock(return_value=mock_execute)
        mock_files = Mock()
        mock_files.export = mock_export
        mock_drive_service = Mock()
        mock_drive_service.files.return_value = mock_files
        service = GoogleDriveService(drive_service=mock_drive_service)

        with pytest.raises(exceptions.GoogleDriveFileNotFoundError, match="Resource not found during reading file."):
            service.read_file('invalid_file')

    def test_read_file_other_http_error(self) -> None:
        """Raises GoogleDriveAPIError on unexpected server errors."""
        error_json = b'{"error": {"message": "Server error"}}'
        mock_execute = Mock()
        mock_execute.execute.side_effect = HttpError(resp=Mock(status=500), content=error_json)
        mock_export = Mock(return_value=mock_execute)
        mock_files = Mock()
        mock_files.export = mock_export
        mock_drive_service = Mock()
        mock_drive_service.files.return_value = mock_files
        service = GoogleDriveService(drive_service=mock_drive_service)

        with pytest.raises(
            exceptions.GoogleDriveAPIError,
            match="Google Drive API error occurred during reading file: Server error"
        ):
            service.read_file('file123')

    def test_read_file_success(self) -> None:
        """Returns decoded content when file read is successful."""
        mock_execute = Mock()
        mock_execute.execute.return_value = b'File content'
        mock_export = Mock(return_value=mock_execute)
        mock_files = Mock()
        mock_files.export = mock_export
        mock_drive_service = Mock()
        mock_drive_service.files.return_value = mock_files
        service = GoogleDriveService(drive_service=mock_drive_service)

        result = service.read_file('file123')

        assert result == 'File content'
        mock_export.assert_called_once_with(fileId='file123', mimeType='text/plain')


@pytest.mark.api
@pytest.mark.admin_upload_blog_posts
class TestReadFileRealAPI:
    """Integration tests for read_file() using real Google Drive API."""

    def test_read_file_not_found(self, google_drive_service_fixture: GoogleDriveService) -> None:
        """Raises GoogleDriveFileNotFoundError when file does not exist."""
        with pytest.raises(exceptions.GoogleDriveFileNotFoundError) as exc_info:
            google_drive_service_fixture.read_file('non_existent_file_id')

        assert "Resource not found" in str(exc_info.value)

    def test_read_file_permission_denied(
            self,
            google_drive_service_fixture: GoogleDriveService,
            test_drive_file_metadata_map: dict
    ) -> None:
        """Raises GoogleDriveFileNotFoundError if file is restricted (API returns 404)."""
        restricted_file_id = test_drive_file_metadata_map["restricted"]["file_id"]

        with pytest.raises(exceptions.GoogleDriveFileNotFoundError) as exc_info:
            google_drive_service_fixture.read_file(restricted_file_id)

        assert "Resource not found" in str(exc_info.value)

    def test_read_file_success(
            self,
            google_drive_service_fixture: GoogleDriveService,
            test_drive_file_metadata_map: dict
    ) -> None:
        """Reads content of a file given a valid file ID."""
        file_id = test_drive_file_metadata_map["design_principles"]["file_id"]

        content = google_drive_service_fixture.read_file(file_id)

        assert isinstance(content, str), "Expected file content to be a string."
        assert len(content.strip()) > 0, "File content should not be empty."
