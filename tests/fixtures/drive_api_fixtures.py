"""Fixtures for testing Google Drive service functionality.

This module provides various pytest fixtures to support both unit and integration
tests of the GoogleDriveService class. It includes fixtures for mocking the
Google Drive service, environment variables, service account credentials,
common Google Drive scopes, and retrieving real configuration values such as
the folder ID for blog posts.
"""

from unittest import mock
from unittest.mock import Mock

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
def mock_google_drive_service() -> GoogleDriveService:
    """Creates a mock Google Drive service instance.

    Returns:
        GoogleDriveService: A GoogleDriveService instance with a mocked drive_service.
    """
    mock_drive_service = Mock()
    return GoogleDriveService(drive_service=mock_drive_service)


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
def scopes() -> list[str]:
    """Fixture for the common Google Drive scopes.

    Returns:
        list[str]: A list of Google Drive OAuth2 scopes.
    """
    return ['https://www.googleapis.com/auth/drive']
