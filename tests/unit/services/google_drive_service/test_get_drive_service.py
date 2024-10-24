"""Unit tests for the _get_drive_service method of the GoogleDriveService class.

This module contains unit tests for the _get_drive_service method, which handles
fetching and caching the Google Drive API service instance. The tests ensure that
the method behaves correctly in various scenarios, such as when a cached service
exists, when authentication is required, or when invalid credentials are provided.

Tests included:
    - test_get_drive_service_with_cached_service: Verifies that the cached service
      is returned when available.
    - test_get_drive_service_without_cached_service: Verifies that the service
      authenticates and caches the drive service when not already set.
    - test_get_drive_service_with_invalid_credentials_path: Verifies that the method
      raises an error when the credentials path is missing or invalid.

Mocks:
    - Mock objects are used to simulate Google Drive API behavior, environment variables,
      and Flask application configuration.
    - Patching is applied to the _authenticate_google_drive method and os.getenv to
      control their behavior during tests.
"""

from unittest.mock import Mock, patch

import pytest

from app import exceptions
from app.services.google_drive_service import GoogleDriveService


@pytest.fixture(autouse=True)
def clear_drive_service_cache():
    """Fixture to clear the drive service cache before each test."""
    GoogleDriveService._cached_drive_service = None

def test_get_drive_service_with_cached_service() -> None:
    """Tests that the cached drive service is returned when available."""
    # Arrange
    mock_cached_service = Mock()
    GoogleDriveService._cached_drive_service = mock_cached_service  # Simulate cached service

    # Act
    service = GoogleDriveService()  # Instantiate without needing to mock
    result = service._get_drive_service()

    # Assert
    assert result == mock_cached_service  # Cached service should be returned
    assert GoogleDriveService._cached_drive_service is mock_cached_service

    # Reset cache after the test
    GoogleDriveService._cached_drive_service = None


@patch('os.getenv')
@patch('flask.current_app')
@patch('app.services.google_drive_service.GoogleDriveService._authenticate_google_drive')
def test_get_drive_service_without_cached_service(
        mock_auth_func: Mock,
        mock_current_app: Mock,
        mock_getenv: Mock,
        app_context_with_mocked_config: None
) -> None:
    """Tests that the drive service is authenticated and cached when not already set."""
    # Arrange
    mock_drive_service = Mock()
    mock_auth_func.return_value = mock_drive_service  # Simulate authenticated service
    mock_getenv.side_effect = lambda \
        key: '/path/to/credentials.json' if key == 'GOOGLE_CREDENTIALS_FILE' else None
    mock_current_app.config.get.return_value = ['https://www.googleapis.com/auth/drive']

    # Act
    service = GoogleDriveService()
    result = service._get_drive_service()

    # Assert
    assert result == mock_drive_service  # Authenticated service should be returned
    assert GoogleDriveService._cached_drive_service == mock_drive_service  # Cache should be set
    mock_auth_func.assert_called_once_with('/path/to/credentials.json',
                                           ['https://www.googleapis.com/auth/drive'])


@patch('os.getenv')
@patch('flask.current_app')
@patch('app.services.google_drive_service.GoogleDriveService._authenticate_google_drive')
def test_get_drive_service_with_invalid_credentials_path(
        mock_auth_func: Mock,
        mock_current_app: Mock,
        mock_getenv: Mock,
        app_context_with_mocked_config: None
) -> None:
    """Tests that the function handles missing or invalid credentials path."""
    # Arrange
    mock_getenv.return_value = None  # Simulate missing environment variable for credentials path
    mock_current_app.config.get.return_value = ['https://www.googleapis.com/auth/drive']

    # Simulate that the authentication function will raise the exception
    mock_auth_func.side_effect = exceptions.GoogleDriveAuthenticationError(
        "Credentials file path is missing or invalid."
    )

    # Act & Assert
    with pytest.raises(exceptions.GoogleDriveAuthenticationError):
        service = GoogleDriveService()
        service._get_drive_service()  # Explicitly call the method to trigger authentication

    # Ensure the authentication method was called with None for the credentials path
    mock_auth_func.assert_called_once_with(None, ['https://www.googleapis.com/auth/drive'])
