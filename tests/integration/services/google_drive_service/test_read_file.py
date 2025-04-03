"""Integration tests for the read_file method of the GoogleDriveService class.

This module contains integration tests for the read_file method of the
GoogleDriveService class, focusing on interactions with the actual Google Drive API.
The tests verify that the service handles successful operations and errors as expected
when communicating with Google Drive.

Tests included:
    - test_read_file_not_found: Verifies that a non-existent file ID raises
      GoogleDriveFileNotFoundError.
    - test_read_file_permission_denied: Verifies that insufficient permissions
      raise GoogleDriveFileNotFoundError.
    - test_read_file_success: Verifies that reading a file with a valid ID returns
      its content correctly.

Fixtures:
    - google_drive_service_fixture: Provides an instance of the real
      GoogleDriveService class for testing.
"""

import pytest

from app import exceptions
from app.services.google_drive_service import GoogleDriveService

DEFAULT_TEST_FILE_ID = '1p5jpGiSa1KyXbQrAEJ44NEBP4pgsLqpsdgYUkMgy3Vo'
RESTRICTED_FILE_ID = '1LafXfqIfye5PLvwnXpAs0brp8C3qvh81sDI--rG7eSk'


@pytest.mark.admin_upload_post
def test_read_file_not_found(
        google_drive_service_fixture: GoogleDriveService
) -> None:
    """Tests that reading a non-existent file raises an error."""
    with pytest.raises(exceptions.GoogleDriveFileNotFoundError) as exc_info:
        google_drive_service_fixture.read_file('non_existent_file_id')
    assert "Resource not found" in str(exc_info.value), \
        "Expected GoogleDriveFileNotFoundError for a non-existent file."


@pytest.mark.admin_upload_post
def test_read_file_permission_denied(
        google_drive_service_fixture: GoogleDriveService
) -> None:
    """Tests that insufficient permissions raise a GoogleDriveFileNotFoundError.

    Google Drive API returns a 404 'File not found' error even when the file exists
    but is inaccessible due to insufficient permissions.
    """
    with pytest.raises(exceptions.GoogleDriveFileNotFoundError) as exc_info:
        google_drive_service_fixture.read_file(RESTRICTED_FILE_ID)
    assert "Resource not found" in str(exc_info.value), \
        "Expected GoogleDriveFileNotFoundError for a file with insufficient permissions."


@pytest.mark.admin_upload_post
def test_read_file_success(
        google_drive_service_fixture: GoogleDriveService
) -> None:
    """Tests reading the contents of a file with a valid file ID."""
    file_content = google_drive_service_fixture.read_file(DEFAULT_TEST_FILE_ID)
    assert isinstance(file_content, str), "Expected file content to be a string."
    print(file_content)
    assert len(file_content) > 0, "File content should not be empty."
