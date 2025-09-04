"""Unit tests for the _get_drive_service method of the GoogleDriveService class.

This module verifies the behavior of the _get_drive_service method, which handles
authentication and caching of the Google Drive service instance.

Test scenarios include:
    - Returning a previously cached service
    - Authenticating and caching the service if no cached instance exists
    - Raising an error when the service account JSON is invalid
"""

from unittest.mock import Mock

import pytest

from app import exceptions
from app.services.google_drive_service import GoogleDriveService


class TestGetDriveService:
    def teardown_method(self) -> None:
        # Clear cache after each test to ensure isolation
        GoogleDriveService._cached_drive_service = None

    def test_get_drive_service_returns_cached_instance(self):
        """Returns the cached drive service if already set."""
        cached_service = Mock()
        GoogleDriveService._cached_drive_service = cached_service

        service = GoogleDriveService()
        result = service._get_drive_service()

        assert result is cached_service

    def test_get_drive_service_authenticates_and_caches_if_not_set(self, mocker, app):
        """Authenticates and caches the drive service if no cache exists."""
        mock_drive_service = Mock()
        mock_auth = mocker.patch(
            'app.services.google_drive_service.GoogleDriveService._authenticate_google_drive',
            return_value=mock_drive_service
        )

        # Clear cache to simulate a fresh call
        GoogleDriveService.clear_cache()

        service = GoogleDriveService()
        result = service._get_drive_service()

        assert result is mock_drive_service
        assert GoogleDriveService._cached_drive_service is mock_drive_service
        mock_auth.assert_called_once_with(
            app.config['GOOGLE_SERVICE_ACCOUNT_JSON'],
            app.config['GOOGLE_DRIVE_SCOPES']
        )

        def test_get_drive_service_raises_error_on_invalid_json(self, mocker, app):
            """Raises an authentication error if the credentials JSON is invalid."""
            invalid_json = {"type": "service_account", "project_id": "missing_closing_brace"}
            mocker.patch(
                'app.services.google_drive_service.current_app.config.get',
                side_effect=lambda key, default=None: (
                    invalid_json if key == 'GOOGLE_SERVICE_ACCOUNT_JSON'
                    else ['https://www.googleapis.com/auth/drive']
                )
            )

            service = GoogleDriveService()

            with pytest.raises(exceptions.GoogleDriveAuthenticationError):
                service._get_drive_service()
