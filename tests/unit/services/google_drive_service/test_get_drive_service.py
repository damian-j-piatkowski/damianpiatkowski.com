"""
Unit tests for the _get_drive_service method of the GoogleDriveService class.

This module contains unit tests for the _get_drive_service method, which handles
fetching and caching the Google Drive API service instance. The tests ensure that
the method behaves correctly in various scenarios, such as when a cached service
exists, when authentication is required, or when invalid JSON credentials are provided.

Tests included:
    - test_get_drive_service_with_cached_service: Verifies that the cached service
      is returned when available.
    - test_get_drive_service_without_cached_service: Verifies that the service
      authenticates and caches the drive service when not already set, using
      configuration values from Flask's current_app.
    - test_get_drive_service_with_invalid_credentials_json: Verifies that the method
      raises an error when the GOOGLE_SERVICE_ACCOUNT_JSON configuration contains
      invalid JSON.

Mocks:
    - Mock objects are used to simulate Google Drive API behavior and Flask application
      configuration.
    - Patching is applied to the _authenticate_google_drive method and current_app to
      control their behavior during tests.
"""

import json
from unittest.mock import Mock, patch

import pytest

from app import exceptions
from app.services.google_drive_service import GoogleDriveService


@pytest.mark.usefixtures("app_context_with_mocked_config")
class TestGetDriveService:
    def teardown_method(self) -> None:
        # Reset the cached service to avoid interference between tests
        GoogleDriveService._cached_drive_service = None

    @patch('flask.current_app')
    @patch('app.services.google_drive_service.GoogleDriveService._authenticate_google_drive')
    def test_get_drive_service_with_cached_service(
        self,
        mock_auth_func: Mock,
        mock_current_app: Mock,
    ) -> None:
        """Tests that the cached drive service is returned when available."""
        mock_cached_service = Mock()
        GoogleDriveService._cached_drive_service = mock_cached_service

        service = GoogleDriveService()
        result = service._get_drive_service()

        assert result == mock_cached_service
        assert GoogleDriveService._cached_drive_service is mock_cached_service
        mock_auth_func.assert_not_called()

    def test_get_drive_service_without_cached_service(self, mocker):
        """Tests that the drive service is authenticated and cached if not already."""
        mock_drive_service = mocker.Mock()
        mock_auth_func = mocker.patch(
            'app.services.google_drive_service.GoogleDriveService._authenticate_google_drive',
            return_value=mock_drive_service
        )

        # Patch current_app.config
        mock_config = {
            'GOOGLE_SERVICE_ACCOUNT_JSON': {'type': 'service_account', 'project_id': 'test'},
            'GOOGLE_DRIVE_SCOPES': ['https://www.googleapis.com/auth/drive']
        }
        mocker.patch('app.services.google_drive_service.current_app').config = mock_config

        # Clear cached service before test
        GoogleDriveService.clear_cache()

        service = GoogleDriveService()
        result = service._get_drive_service()

        assert result == mock_drive_service
        assert GoogleDriveService._cached_drive_service == mock_drive_service
        mock_auth_func.assert_called_once_with(
            {'type': 'service_account', 'project_id': 'test'},
            ['https://www.googleapis.com/auth/drive']
        )

    @patch('flask.current_app')
    def test_get_drive_service_with_invalid_credentials_json(
            self,
            mock_current_app: Mock,
    ) -> None:
        """Tests that invalid JSON in GOOGLE_SERVICE_ACCOUNT_JSON raises an error."""
        invalid_json_str = '{"type": "service_account", "project_id": "test"'  # missing closing }

        mock_current_app.config.get.side_effect = lambda key, default=None: (
            invalid_json_str if key == 'GOOGLE_SERVICE_ACCOUNT_JSON'
            else ['https://www.googleapis.com/auth/drive']
        )

        with pytest.raises(exceptions.GoogleDriveAuthenticationError):
            service = GoogleDriveService()
            service._get_drive_service()
