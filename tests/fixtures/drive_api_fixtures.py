"""Fixtures for testing Google Drive service functionality.

This module provides various pytest fixtures to support both unit and integration
tests of the GoogleDriveService class. It includes fixtures for mocking the
Google Drive service, environment variables, service account credentials,
common Google Drive scopes, and retrieving real configuration values such as
the folder ID for blog posts.
"""

from datetime import datetime, timezone
from unittest import mock
from unittest.mock import Mock, MagicMock
from app import exceptions

from freezegun import freeze_time
import datetime as dt
import pytest
from google.oauth2.service_account import Credentials as ServiceAccountCredentials

from app.services.google_drive_service import GoogleDriveService


@pytest.fixture
def google_drive_service_fixture(app) -> GoogleDriveService:
    """Provides an instance of GoogleDriveService for integration testing.

    Args:
        app: The Flask app fixture.

    Returns:
        GoogleDriveService: An instance of the GoogleDriveService class.
    """
    return GoogleDriveService()


@pytest.fixture
def mock_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mocks environment variables used in the method.

    Args:
        monkeypatch: pytest's monkeypatch fixture to mock environment variables.
    """
    monkeypatch.setenv('GOOGLE_CREDENTIALS_FILE', '/fake/credentials.json')


@pytest.fixture
def mock_google_drive_service(mocker, request) -> MagicMock:
    """Creates a mock Google Drive service instance with extended functionality."""
    # Create a mock for the GoogleDriveService class
    mock_google_drive_service = mocker.Mock(spec=GoogleDriveService)

    # Patch the instantiation in the process_file function to return the mock
    mocker.patch(
        "app.services.file_processing_service.GoogleDriveService",
        return_value=mock_google_drive_service
    )

    # Preconfigure default behaviors for the mock methods
    mock_google_drive_service.list_folder_contents.return_value = [
        {"id": "1", "name": "Mock File", "mimeType": "application/vnd.google-apps.document"}
    ]
    mock_google_drive_service.read_file.return_value = "Mock file content"

    # Allow test-specific overrides of read_file.side_effect via request.param
    if hasattr(request, "param"):
        # Apply test-specific side effects
        if "read_file_side_effect" in request.param:
            mock_google_drive_service.read_file.side_effect = request.param["read_file_side_effect"]
            print(f"Configured read_file.side_effect: {request.param['read_file_side_effect']}")  # Debug
        # Apply test-specific list folder return values
        if "list_folder_contents_return" in request.param:
            mock_google_drive_service.list_folder_contents.return_value = request.param["list_folder_contents_return"]
            print(f"Configured list_folder_contents.return_value: {request.param['list_folder_contents_return']}")  # Debug

    # Debug output for mock service methods
    print(f"Default list_folder_contents.return_value: {mock_google_drive_service.list_folder_contents.return_value}")
    print(f"Default read_file.return_value: {mock_google_drive_service.read_file.return_value}")

    return mock_google_drive_service





@pytest.fixture
def mock_service_account_creds() -> Mock:
    """Mocks the service account credentials object.

    Returns:
        Mock: A mock object representing service account credentials.
    """
    return mock.create_autospec(ServiceAccountCredentials)


@pytest.fixture
def real_folder_id(app) -> str:
    """Retrieves the real folder ID from the app configuration.

    Args:
        app: The Flask app fixture.

    Returns:
        str: The folder ID for storing blog posts.
    """
    return app.config.get('DRIVE_BLOG_POSTS_FOLDER_ID')

@pytest.fixture
def real_drive_file_metadata():
    """Returns a known Google Drive file's ID along with extracted slug and title."""
    return {
    "file_id": "1p5jpGiSa1KyXbQrAEJ44NEBP4pgsLqpsdgYUkMgy3Vo",
    "slug": "six-essential-object-oriented-design-principles-from-matthias-nobacks-object-design-style-guide",
    "title": "Six Essential Object Oriented Design Principles From Matthias Nobacks Object Design Style Guide",
    }

@pytest.fixture
def restricted_drive_file_metadata():
    """Returns metadata for a real Google Drive file that is NOT accessible to the bot."""
    return {
        "file_id": "1LafXfqIfye5PLvwnXpAs0brp8C3qvh81sDI--rG7eSk",
        "slug": "test-restricted-access",
        "title": "Test Restricted Access",
    }

@pytest.fixture
def another_drive_file_metadata():
    """Fixture providing metadata for a different real Google Drive file."""
    return {
        "file_id": "187rlFKQsACliz_ta-niIgK9ZDOwsR9a3YmfrkbX_R1E",
        "title": "Value Objects",
        "slug": "value-objects",
    }

@pytest.fixture(scope='function')
def valid_file_data():
    """Fixture providing valid file data for blog post file processing tests.

    This dictionary includes:
    - A sample file_id as it would come from Google Drive
    - A title used for the blog post
    - A slug derived from the title
    """
    return {
        'file_id': '12345',
        'title': 'Test Blog Post',
        'slug': 'test-blog-post'
    }


@pytest.fixture
def scopes() -> list[str]:
    """Fixture for the common Google Drive scopes.

    Returns:
        list[str]: A list of Google Drive OAuth2 scopes.
    """
    return ['https://www.googleapis.com/auth/drive']
