import json
from typing import List, Dict
from unittest import mock
from unittest.mock import MagicMock

import pytest

from app.services.google_drive_service import GoogleDriveService


# Fixture to mock the environment variables for service account
@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("GOOGLE_DRIVE_SCOPES",
                       '["https://www.googleapis.com/auth/drive"]')
    monkeypatch.setenv("GOOGLE_PROJECT_ID", "my-project-id")
    monkeypatch.setenv("GOOGLE_PRIVATE_KEY_ID", "my-private-key-id")
    monkeypatch.setenv("GOOGLE_PRIVATE_KEY", "my-private-key")
    monkeypatch.setenv("GOOGLE_CLIENT_EMAIL",
                       "my-client-email@my-project-id.iam.gserviceaccount.com")
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "my-client-id")
    monkeypatch.setenv("GOOGLE_TOKEN_FILE", "test_token.json")


# Fixture to mock the token.json file with valid credentials
@pytest.fixture
def mock_valid_token():
    with mock.patch("builtins.open",
                    mock.mock_open(read_data='{"token": "valid-token"}')), \
            mock.patch("os.path.exists", return_value=True), \
            mock.patch(
                "google.oauth2.credentials.Credentials.from_authorized_user_file") as mock_creds:
        mock_creds.return_value = mock.Mock(valid=True, expired=False)
        yield mock_creds


# Fixture to mock the token.json file with expired credentials and refresh token available
@pytest.fixture
def mock_expired_token():
    mock_creds = mock.Mock(valid=False, expired=True,
                           refresh_token="refresh-token")
    with mock.patch("builtins.open",
                    mock.mock_open(read_data='{"token": "expired-token"}')), \
            mock.patch("os.path.exists", return_value=True), \
            mock.patch(
                "google.oauth2.credentials.Credentials.from_authorized_user_file",
                return_value=mock_creds), \
            mock.patch("google.auth.transport.requests.Request"):
        yield mock_creds


# Fixture to mock the service account credentials
@pytest.fixture
def mock_service_account_creds():
    mock_creds = mock.Mock(valid=True)
    with mock.patch(
            "google.oauth2.service_account.Credentials.from_service_account_file",
            return_value=mock_creds):
        yield mock_creds


@pytest.fixture
def create_token_file(tmp_path) -> str:
    """Fixture to create a mock token.json file with default data."""
    default_data = {
        "token": "valid-token",
        "refresh_token": "valid-refresh-token",
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": "test-client-id",
        "client_secret": "test-client-secret",
        "scopes": ['https://www.googleapis.com/auth/drive.readonly']
    }

    # Create token.json in the provided tmp_path
    token_file_path = tmp_path / "token.json"
    with open(token_file_path, 'w') as token_file:
        json.dump(default_data, token_file)

    yield token_file_path  # Yield the path to the test

    # Cleanup is handled by tmp_path, no need for manual os.remove


# @pytest.fixture
# def drive_service():
#     """Fixture to initialize the real GoogleDriveService (for integration tests)."""
#     return GoogleDriveService()


@pytest.fixture
def mock_drive_service(mocker):
    """Fixture to initialize a mocked GoogleDriveService (for unit tests)."""
    mock_service = MagicMock(spec=GoogleDriveService)

    # Mock list_files_in_drive method
    mock_service.list_files_in_drive.return_value = [
        {'id': '1', 'name': 'Mock File 1'},
        {'id': '2', 'name': 'Mock File 2'},
    ]

    # Mock read_file method
    mock_service.read_file.return_value = "This is mock file content"

    return mock_service


@pytest.fixture
def mock_drive_docs() -> List[Dict[str, str]]:
    """Fixture to create mock Google Drive documents."""
    return [
        {'name': 'Post 1'},
        {'name': 'Post 2'},
        {'name': 'Post 4'},  # Post 4 is in Drive but not in DB
    ]


# @pytest.fixture
# def mock_env_vars(monkeypatch):
#     """Set mock environment variables."""
#     monkeypatch.setenv('GOOGLE_CLIENT_ID', 'test-client-id')
#     monkeypatch.setenv('GOOGLE_CLIENT_SECRET', 'test-client-secret')
#     monkeypatch.setenv('GOOGLE_PROJECT_ID', 'test-project-id')
