"""Unit tests for the clear_cache method of the GoogleDriveService class.

This module contains a unit test for the clear_cache method, which resets the
cached Google Drive service instance. The test verifies that the cache is
successfully cleared after it is manually set.

Tests included:
    - test_clear_cache: Verifies that the cached drive service is cleared after
      calling the clear_cache method.

Mocks:
    - No external services are mocked in this test since it only deals with
      internal caching behavior of the GoogleDriveService class.
"""

from app.services.google_drive_service import GoogleDriveService


def test_clear_cache() -> None:
    """Tests that the clear_cache method clears the cached drive service.

    Manually sets the _cached_drive_service class attribute to simulate the
    cache being set after authentication and asserts that it is cleared after
    calling clear_cache.
    """
    # Manually set the cache to simulate the cache being set after authentication
    GoogleDriveService._cached_drive_service = 'fake_drive_service'

    # Verify the cache is set
    assert GoogleDriveService._cached_drive_service == 'fake_drive_service'

    # Initialize the service (in this case, the drive_service doesn't matter)
    service = GoogleDriveService()

    # Call clear_cache and check if the cache is cleared
    service.clear_cache()

    # Assert that the cache is cleared
    assert GoogleDriveService._cached_drive_service is None
