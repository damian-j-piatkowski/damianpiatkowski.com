"""Fixtures for testing Google Drive service functionality.

This module provides various pytest fixtures to support both unit and integration
tests of the GoogleDriveService class. It includes fixtures for mocking the
Google Drive service, environment variables, service account credentials,
common Google Drive scopes, and retrieving real configuration values such as
the folder ID for blog posts.

Fixtures:
    - google_drive_service_fixture
    - mock_env
    - mock_google_drive_service
    - mock_service_account_creds
    - real_folder_id
    - test_drive_file_metadata_map
    - scopes
"""

from unittest import mock
from unittest.mock import Mock, MagicMock

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
            print(
                f"Configured list_folder_contents.return_value: {request.param['list_folder_contents_return']}")  # Debug

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
def test_drive_file_metadata_map():
    """Returns a dict of test Google Drive file metadata keyed by human-readable aliases."""
    return {
        "design_principles": {
            "file_id": "1p5jpGiSa1KyXbQrAEJ44NEBP4pgsLqpsdgYUkMgy3Vo",
            "slug": "six-essential-object-oriented-design-principles-from-matthias-nobacks-object-design-style-guide",
            "title": "Six Essential Object Oriented Design Principles From Matthias Nobacks Object Design Style Guide",
        },
        "value_objects": {
            "file_id": "187rlFKQsACliz_ta-niIgK9ZDOwsR9a3YmfrkbX_R1E",
            "slug": "value-objects",
            "title": "Value Objects",
        },
        "value_objects_test": {
            "file_id": "1e8CUUM6S3ZXRXIhoE0oxM_4O5eqH1mr5YyoiWzjpWxI",
            "slug": "value-objects-test",
            "title": "Value Objects Test",
        },
        "markdown_to_html": {
            "file_id": "1zZM1zY6qmOIuXh2Fb-6oQ3lZ_ETRvEnlnl75Pw3WecE",
            "slug": "markdown-to-html-test",
            "title": "Markdown To Html Test",
        },
        "restricted": {
            "file_id": "1LafXfqIfye5PLvwnXpAs0brp8C3qvh81sDI--rG7eSk",
            "slug": "test-restricted-access",
            "title": "Test Restricted Access",
        },
    }


@pytest.fixture
def scopes() -> list[str]:
    """Fixture for the common Google Drive scopes.

    Returns:
        list[str]: A list of Google Drive OAuth2 scopes.
    """
    return ['https://www.googleapis.com/auth/drive']
