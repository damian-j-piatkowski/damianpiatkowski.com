from unittest import mock

import pytest
from google.oauth2.service_account import Credentials as ServiceAccountCredentials

from app.services.google_drive_service import GoogleDriveService
from app.services import exceptions


@pytest.fixture
def mock_env(monkeypatch):
    """Mock environment variables used in the method."""
    monkeypatch.setenv('GOOGLE_CREDENTIALS_FILE', '/fake/credentials.json')


@pytest.fixture
def mock_service_account_creds():
    """Mock the service account credentials object."""
    return mock.create_autospec(ServiceAccountCredentials)


@pytest.fixture
def scopes():
    """Fixture for the common Google Drive scopes."""
    return ['https://www.googleapis.com/auth/drive']


def test_authenticate_with_service_account_creds(mock_env, mock_service_account_creds, scopes):
    """Test authentication using service account credentials."""
    # Mock the `with_scopes` method to return the credentials itself
    mock_service_account_creds.with_scopes.return_value = mock_service_account_creds

    with mock.patch('google.oauth2.service_account.Credentials.from_service_account_file',
                    return_value=mock_service_account_creds), \
            mock.patch('app.services.google_drive_service.build') as mock_build:
        # Call the method under test
        GoogleDriveService._authenticate_google_drive('/fake/credentials.json', scopes)

        # Assert that build was called with the service account credentials (after with_scopes)
        mock_build.assert_called_once_with('drive', 'v3', credentials=mock_service_account_creds)

        # Ensure that with_scopes() was called with the provided scopes
        mock_service_account_creds.with_scopes.assert_called_once_with(scopes)


def test_authenticate_without_credentials_file(mock_env, mock_service_account_creds, scopes):
    """Test authentication when no credentials file is provided."""
    with pytest.raises(exceptions.GoogleDriveAuthenticationError, match="Credentials file path is missing or invalid."):
        # Call the method with no credentials file, expecting a GoogleDriveAuthenticationError
        GoogleDriveService._authenticate_google_drive(None, scopes)


def test_authenticate_with_invalid_credentials_file(mock_env, mock_service_account_creds, scopes):
    """Test authentication with an invalid credentials file."""
    with mock.patch('google.oauth2.service_account.Credentials.from_service_account_file') as mock_creds_loader:
        # Simulate an error when trying to load invalid credentials
        mock_creds_loader.side_effect = FileNotFoundError("Credentials file not found")

        with pytest.raises(exceptions.GoogleDriveAuthenticationError, match="File not found: Credentials file not found"):
            # Call the method under test
            GoogleDriveService._authenticate_google_drive('/invalid/path/credentials.json', scopes)


def test_authenticate_with_google_api_error(mock_env, mock_service_account_creds, scopes):
    """Test authentication when the Google API raises an HttpError."""
    from googleapiclient.errors import HttpError

    with mock.patch('google.oauth2.service_account.Credentials.from_service_account_file',
                    return_value=mock_service_account_creds), \
            mock.patch('app.services.google_drive_service.build') as mock_build:
        # Simulate an HttpError during build
        mock_build.side_effect = HttpError(mock.Mock(), b"Google API error")

        with pytest.raises(exceptions.GoogleDriveAPIError, match="Google API error during authentication"):
            GoogleDriveService._authenticate_google_drive('/fake/credentials.json', scopes)
