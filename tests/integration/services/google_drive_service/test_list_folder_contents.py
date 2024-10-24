"""Integration tests for the list_folder_contents method of the GoogleDriveService class.

This module contains integration tests for the list_folder_contents method
of the GoogleDriveService class, focusing on interactions with the actual Google Drive API.
The tests verify that the service handles successful operations and errors as expected
when communicating with Google Drive.

Tests included:
    - test_list_folder_contents_not_found: Verifies that a non-existent folder ID raises
      GoogleDriveFileNotFoundError.
    - test_list_folder_contents_success: Verifies successful retrieval of folder
      contents with a valid folder ID.

Fixtures:
    - google_drive_service_fixture: Provides an instance of the real
      GoogleDriveService class for testing.
    - real_folder_id: Provides the actual folder ID from the app configuration.
"""

import pytest

from app import exceptions
from app.services.google_drive_service import GoogleDriveService


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
