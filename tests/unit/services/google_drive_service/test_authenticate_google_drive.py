"""Unit tests for the _authenticate_google_drive method of the GoogleDriveService class.

This module tests the _authenticate_google_drive method, which handles authentication
for the Google Drive API using service account credentials passed as a dictionary
(rather than from a JSON file).

Tests included:
    - test_authenticate_with_service_account_info: Verifies successful authentication.
    - test_authenticate_with_missing_info: Verifies error when credentials info is missing.
    - test_authenticate_with_invalid_info: Verifies error when credentials info is invalid.
    - test_authenticate_with_google_api_error: Verifies handling of Google API errors.

Mocks:
    - google.oauth2.service_account.Credentials.from_service_account_info
    - Google Drive API build function.
"""

from unittest import mock

import pytest
from googleapiclient.errors import HttpError

from app import exceptions
from app.services.google_drive_service import GoogleDriveService


def test_authenticate_with_service_account_info(
        fake_service_account_credentials_json,
        mock_service_account_creds,
        scopes
) -> None:
    """Verifies successful authentication."""
    mock_service_account_creds.with_scopes.return_value = mock_service_account_creds

    with mock.patch('google.oauth2.service_account.Credentials.from_service_account_info',
                    return_value=mock_service_account_creds), \
            mock.patch('app.services.google_drive_service.build') as mock_build:
        GoogleDriveService._authenticate_google_drive(fake_service_account_credentials_json, scopes)

        mock_build.assert_called_once_with('drive', 'v3', credentials=mock_service_account_creds)
        mock_service_account_creds.with_scopes.assert_called_once_with(scopes)


def test_authenticate_with_missing_info(scopes) -> None:
    """Verifies error when credentials info is missing."""
    with pytest.raises(exceptions.GoogleDriveAuthenticationError,
                       match="Service account info is missing or invalid."):
        GoogleDriveService._authenticate_google_drive(None, scopes)  # type: ignore[arg-type]


def test_authenticate_with_invalid_info(mock_service_account_creds, scopes) -> None:
    """Verifies error when credentials info is invalid."""
    with mock.patch('google.oauth2.service_account.Credentials.from_service_account_info') as mock_loader:
        mock_loader.side_effect = ValueError("Invalid credentials info")

        with pytest.raises(exceptions.GoogleDriveAuthenticationError,
                           match="Invalid credentials: Invalid credentials info"):
            GoogleDriveService._authenticate_google_drive({'invalid': 'data'}, scopes)


def test_authenticate_with_google_api_error(
        fake_service_account_credentials_json,
        mock_service_account_creds,
        scopes
) -> None:
    """Verifies handling of Google API errors."""
    mock_service_account_creds.with_scopes.return_value = mock_service_account_creds

    with mock.patch('google.oauth2.service_account.Credentials.from_service_account_info',
                    return_value=mock_service_account_creds), \
            mock.patch('app.services.google_drive_service.build') as mock_build:
        mock_build.side_effect = HttpError(mock.Mock(), b"Google API error")

        with pytest.raises(exceptions.GoogleDriveAPIError,
                           match="Google API error during authentication"):
            GoogleDriveService._authenticate_google_drive(fake_service_account_credentials_json, scopes)
