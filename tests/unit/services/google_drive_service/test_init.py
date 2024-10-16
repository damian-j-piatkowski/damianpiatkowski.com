"""Unit tests for the constructor of the GoogleDriveService class.

This module contains unit tests specifically for the __init__ method of the
GoogleDriveService class, which handles the initialization of a Google Drive
API service instance. The tests ensure correct behavior when using pre-authenticated
services or when requiring authentication.

Tests included:
    - test_init_with_pre_authenticated_service: Verifies that a pre-authenticated
      drive_service is used when passed to the constructor.
    - test_init_without_pre_authenticated_service: Verifies that the service
      authenticates a new drive_service when none is provided.
    - test_init_raises_assertion_error: Verifies that an AssertionError is raised
      when drive service initialization fails.

Mocks:
    - Mock objects are used to simulate Google Drive API behavior and authentication.
    - Patching is applied to the _get_drive_service method to control its output
      during tests.
"""

from unittest.mock import Mock, patch

import pytest

from app.services.google_drive_service import GoogleDriveService


@patch('app.services.google_drive_service.GoogleDriveService._get_drive_service')
def test_init_with_pre_authenticated_service(mock_get_drive_service: Mock) -> None:
    """Tests that the init method uses a pre-authenticated service if provided."""
    # Arrange
    mock_drive_service = Mock()

    # Act
    google_drive_service = GoogleDriveService(drive_service=mock_drive_service)

    # Assert, pre-authenticated service should be used
    assert google_drive_service.drive_service is mock_drive_service
    mock_get_drive_service.assert_not_called()  # _get_drive_service should not be called


@patch('app.services.google_drive_service.GoogleDriveService._get_drive_service')
def test_init_without_pre_authenticated_service(mock_get_drive_service: Mock) -> None:
    """Tests that the init method authenticates a new service if no service is provided."""
    # Arrange
    mock_drive_service = Mock()
    mock_get_drive_service.return_value = mock_drive_service  # Simulate authenticated service

    # Act
    google_drive_service = GoogleDriveService()

    # Assert, authenticated service should be used
    assert google_drive_service.drive_service is mock_drive_service
    mock_get_drive_service.assert_called_once()  # _get_drive_service should be called


@patch('app.services.google_drive_service.GoogleDriveService._get_drive_service')
def test_init_raises_assertion_error(mock_get_drive_service: Mock) -> None:
    """Tests that the init raises an assertion error if drive service initialization fails."""
    # Arrange
    mock_get_drive_service.return_value = None  # Simulate authentication failure

    # Act & Assert
    with pytest.raises(AssertionError, match="Drive service initialization failed."):
        GoogleDriveService()
