"""Integration tests for GoogleDriveService class methods.

This module contains integration tests for the methods of the GoogleDriveService
class, focusing on interactions with the actual Google Drive API. The tests verify
that the service handles successful operations and errors as expected when
communicating with Google Drive.

Tests included:
    - test_list_folder_contents_success: Verifies successful retrieval of folder
      contents with a valid folder ID.
    - test_list_folder_contents_not_found: Verifies that a non-existent folder ID
      raises GoogleDriveFileNotFoundError.
    - test_read_file_success: Verifies that reading a file with a valid ID returns
      its content correctly.
    - test_read_file_not_found: Verifies that a non-existent file ID raises
      GoogleDriveFileNotFoundError.
    - test_read_file_permission_denied: Verifies that insufficient permissions
      raise GoogleDriveFileNotFoundError.

Fixtures:
    - google_drive_service_fixture: Provides an instance of the real
      GoogleDriveService class for testing.
    - real_folder_id: Provides the actual folder ID from the app configuration.
"""

import pytest

from app.services import exceptions
from app.services.google_drive_service import GoogleDriveService

DEFAULT_TEST_FILE_ID = '1p5jpGiSa1KyXbQrAEJ44NEBP4pgsLqpsdgYUkMgy3Vo'
RESTRICTED_FILE_ID = '1LafXfqIfye5PLvwnXpAs0brp8C3qvh81sDI--rG7eSk'


@pytest.fixture
def google_drive_service_fixture(app) -> GoogleDriveService:
    """Fixture to provide an instance of GoogleDriveService for integration testing."""
    from app.services.google_drive_service import GoogleDriveService
    return GoogleDriveService()


@pytest.fixture
def real_folder_id(app) -> str:
    """Fixture to retrieve the real folder ID from the app configuration."""
    return app.config.get('DRIVE_BLOG_POSTS_FOLDER_ID')


def test_list_folder_contents_success(
        google_drive_service_fixture: GoogleDriveService,
        real_folder_id: str
) -> None:
    """Tests listing contents of a valid folder ID."""
    folder_contents = google_drive_service_fixture.list_folder_contents(real_folder_id)
    assert isinstance(folder_contents, list), "Expected folder contents to be a list."
    assert all('id' in file and 'name' in file for file in folder_contents), \
        "Each file should contain an 'id' and 'name'."


def test_list_folder_contents_not_found(
        google_drive_service_fixture: GoogleDriveService
) -> None:
    """Tests that listing contents of a non-existent folder raises an error."""
    with pytest.raises(exceptions.GoogleDriveFileNotFoundError) as exc_info:
        google_drive_service_fixture.list_folder_contents('non_existent_folder_id')
    assert "Resource not found during listing folder contents" in str(exc_info.value), \
        "Expected GoogleDriveFileNotFoundError for a non-existent folder."


def test_read_file_success(
        google_drive_service_fixture: GoogleDriveService
) -> None:
    """Tests reading the contents of a file with a valid file ID."""
    file_content = google_drive_service_fixture.read_file(DEFAULT_TEST_FILE_ID)
    assert isinstance(file_content, str), "Expected file content to be a string."
    assert len(file_content) > 0, "File content should not be empty."


def test_read_file_not_found(
        google_drive_service_fixture: GoogleDriveService
) -> None:
    """Tests that reading a non-existent file raises an error."""
    with pytest.raises(exceptions.GoogleDriveFileNotFoundError) as exc_info:
        google_drive_service_fixture.read_file('non_existent_file_id')
    assert "Resource not found" in str(exc_info.value), \
        "Expected GoogleDriveFileNotFoundError for a non-existent file."


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
