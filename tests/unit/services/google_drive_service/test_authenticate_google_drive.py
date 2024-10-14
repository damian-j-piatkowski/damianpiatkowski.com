from unittest import mock

import pytest
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials

from app.services.google_drive_service import GoogleDriveService


@pytest.fixture
def mock_env(monkeypatch):
    """Mock environment variables used in the method."""
    monkeypatch.setenv('GOOGLE_CREDENTIALS_FILE', '/fake/credentials.json')
    monkeypatch.setenv('GOOGLE_TOKEN_FILE', '/fake/token.json')


@pytest.fixture
def mock_creds():
    """Mock the credentials object."""
    return mock.create_autospec(Credentials)


@pytest.fixture
def mock_service_account_creds():
    """Mock the service account credentials object."""
    return mock.create_autospec(ServiceAccountCredentials)


@pytest.fixture
def scopes():
    """Fixture for the common Google Drive scopes."""
    return ['https://www.googleapis.com/auth/drive']


@pytest.fixture
def write_token_file(tmpdir):
    """Helper fixture to write content to a temporary token file."""

    def _write_token(content):
        token_file = tmpdir.join("token.json")
        token_file.write(content)
        return str(token_file)

    return _write_token


@pytest.fixture
def mock_token_file(mock_creds, write_token_file):
    """Mock the existence of a token file with valid credentials."""
    # Mock valid token content
    content = """
    {
        "refresh_token": "fake_refresh_token",
        "client_id": "fake_client_id",
        "client_secret": "fake_client_secret"
    }
    """
    token_file = write_token_file(content)

    mock_creds.expired = False  # Token is not expired
    mock_creds.configure_mock(with_scopes=mock.MagicMock(return_value=mock_creds))

    return token_file


@pytest.fixture
def mock_expired_token_file(mock_creds, write_token_file):
    """Mock the existence of an expired token file."""
    content = """
    {
        "refresh_token": "fake_refresh_token",
        "client_id": "fake_client_id",
        "client_secret": "fake_client_secret"
    }
    """
    token_file = write_token_file(content)

    mock_creds.expired = True  # Token is expired
    mock_creds.refresh_token = "fake_refresh_token"

    return token_file


def test_authenticate_with_token_file_exists(mock_env, mock_creds, scopes, tmpdir):
    """Test authentication when the token file exists and is not expired."""
    # Create a temporary token file in the tmpdir with valid JSON content
    token_file = tmpdir.join("token.json")

    # Mock a valid Google token format
    token_file.write("""
    {
        "refresh_token": "fake_refresh_token",
        "client_id": "fake_client_id",
        "client_secret": "fake_client_secret"
    }
    """)

    # Set up the mock for credentials and discovery
    mock_creds.expired = False  # Ensure the mock token is not expired

    # Manually add the `with_scopes` method to the mock
    mock_creds.configure_mock(with_scopes=mock.MagicMock(return_value=mock_creds))

    with mock.patch('os.path.exists', side_effect=lambda path: path == str(token_file)), \
            mock.patch('google.oauth2.credentials.Credentials.from_authorized_user_file',
                       return_value=mock_creds), \
            mock.patch('google.oauth2.service_account.Credentials.from_service_account_file',
                       return_value=mock_creds), \
            mock.patch('app.services.google_drive_service.build') as mock_build:
        # Call the method under test
        GoogleDriveService._authenticate_google_drive('/fake/credentials.json', str(token_file),
                                                      scopes)

        # Assert that build was called with the correct parameters
        mock_build.assert_called_once_with('drive', 'v3', credentials=mock_creds)


def test_authenticate_with_expired_token(mock_env, mock_creds, scopes, mock_expired_token_file):
    """Test authentication when the token file exists but the token is expired."""
    # Mock the credentials to be expired and have a refresh token
    mock_creds.expired = True
    mock_creds.refresh_token = "fake_refresh_token"

    # Mock the `to_json` method to return a valid JSON string
    mock_creds.to_json.return_value = """
    {
        "refresh_token": "fake_refresh_token",
        "client_id": "fake_client_id",
        "client_secret": "fake_client_secret"
    }
    """

    with mock.patch('os.path.exists', return_value=True), \
            mock.patch('google.oauth2.credentials.Credentials.from_authorized_user_file',
                       return_value=mock_creds), \
            mock.patch('google.auth.transport.requests.Request'), \
            mock.patch('app.services.google_drive_service.build') as mock_build:
        # Call the method under test
        GoogleDriveService._authenticate_google_drive('/fake/credentials.json',
                                                      mock_expired_token_file, scopes)

        # Assert that build was called with the refreshed credentials
        mock_build.assert_called_once_with('drive', 'v3', credentials=mock_creds)

        # Ensure the refresh method was called
        mock_creds.refresh.assert_called_once()

        # Ensure that creds.to_json() was called to write the refreshed credentials
        # back to the token file
        mock_creds.to_json.assert_called_once()


def test_authenticate_without_token_file(mock_env, mock_service_account_creds, scopes):
    """Test authentication when the token file does not exist."""
    # Mock the `with_scopes` method to return the credentials itself
    mock_service_account_creds.with_scopes.return_value = mock_service_account_creds

    with mock.patch('os.path.exists', return_value=False), \
            mock.patch('google.oauth2.service_account.Credentials.from_service_account_file',
                       return_value=mock_service_account_creds), \
            mock.patch('app.services.google_drive_service.build') as mock_build:
        # Call the method under test
        GoogleDriveService._authenticate_google_drive('/fake/credentials.json', None, scopes)

        # Assert that build was called with the service account credentials (after with_scopes)
        mock_build.assert_called_once_with('drive', 'v3', credentials=mock_service_account_creds)

        # Ensure that with_scopes() was called with the provided scopes
        mock_service_account_creds.with_scopes.assert_called_once_with(scopes)


def test_authenticate_with_invalid_token_file(mock_env, mock_creds, scopes, tmpdir):
    """Test authentication when the token file exists but contains invalid content."""
    # Write invalid JSON to the token file
    invalid_token_file = tmpdir.join("token.json")
    invalid_token_file.write("{ invalid_json }")

    with mock.patch('os.path.exists', return_value=True), \
            mock.patch(
                'google.oauth2.credentials.Credentials.from_authorized_user_file'
            ) as mock_creds_loader, \
            mock.patch('app.services.google_drive_service.build'):
        # Simulate an error when trying to load invalid credentials
        mock_creds_loader.side_effect = ValueError("Invalid token file content")

        with pytest.raises(ValueError, match="Invalid token file content"):
            # Call the method under test
            GoogleDriveService._authenticate_google_drive(
                '/fake/credentials.json', str(invalid_token_file), scopes)


def test_authenticate_without_credentials_file(mock_env, mock_service_account_creds, scopes):
    """Test authentication when no credentials file is provided."""
    with pytest.raises(TypeError):
        # Call the method with no credentials file, expecting a TypeError
        GoogleDriveService._authenticate_google_drive(None, None, scopes)


def test_authenticate_expired_no_refresh_token(mock_env, mock_creds, scopes, write_token_file):
    """Test auth fallback to service account when token is expired and no refresh token exists."""
    # Mock a valid Google token format without a refresh token
    token_file = write_token_file("""
    {
        "client_id": "fake_client_id",
        "client_secret": "fake_client_secret"
    }
    """)

    mock_creds.expired = True  # Token is expired
    mock_creds.refresh_token = None  # No refresh token

    with mock.patch('os.path.exists', return_value=True), \
            mock.patch('google.oauth2.credentials.Credentials.from_authorized_user_file',
                       return_value=mock_creds), \
            mock.patch('google.auth.transport.requests.Request'), \
            mock.patch(
                'google.oauth2.service_account.Credentials.from_service_account_file'
            ) as mock_service_account, \
            mock.patch('app.services.google_drive_service.build') as mock_build:
        # Call the method under test
        GoogleDriveService._authenticate_google_drive(
            '/fake/credentials.json', token_file, scopes)

        # Ensure the service account credentials are loaded as a fallback
        mock_service_account.assert_called_once_with('/fake/credentials.json')
        mock_build.assert_called_once()  # Ensure build was called
