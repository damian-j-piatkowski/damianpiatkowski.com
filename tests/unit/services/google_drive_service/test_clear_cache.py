from app.services.google_drive_service import GoogleDriveService


def test_clear_cache():
    # Manually set the cache to simulate the cache being set after authentication
    GoogleDriveService._cached_drive_service = 'fake_drive_service'

    # Verify the cache is set
    assert GoogleDriveService._cached_drive_service == 'fake_drive_service'

    # Initialize the service (in this case, the drive_service doesn't matter)
    service = GoogleDriveService()

    # Call clear_cache and check if the cache is cleared
    service.clear_cache()
    assert GoogleDriveService._cached_drive_service is None  # Cache should be cleared
