"""Pytest fixtures for Google Drive service tests."""

import json
from unittest import mock
from unittest.mock import MagicMock

import pytest
from google.oauth2.service_account import Credentials as ServiceAccountCredentials

from app.services.google_drive_service import GoogleDriveService


@pytest.fixture
def google_drive_service_fixture(app) -> GoogleDriveService:
    """Provides a GoogleDriveService instance with fake service account config."""
    return GoogleDriveService()


@pytest.fixture
def mock_google_drive_service(mocker, request) -> MagicMock:
    """Creates a configurable mock Google Drive service."""
    param = getattr(request, "param", {}) if hasattr(request, "param") else {}
    target_path = param.get("patch_target", "app.services.file_processing_service.GoogleDriveService")

    mock_service = mocker.Mock(spec=GoogleDriveService)
    mocker.patch(target_path, return_value=mock_service)

    mock_service.list_folder_contents.return_value = [
        {"id": "1", "name": "Mock File", "mimeType": "application/vnd.google-apps.document"}
    ]
    mock_service.read_file.return_value = (
        "Title: Test Post\n"
        "Categories: Testing\n"
        "Meta Description: A description.\n"
        "Keywords: test\n\n"
        "+++\n\n"
        "Mock file content."
    )

    if "read_file_side_effect" in param:
        mock_service.read_file.side_effect = param["read_file_side_effect"]
    if "list_folder_contents_side_effect" in param:
        mock_service.list_folder_contents.side_effect = param["list_folder_contents_side_effect"]
    elif "list_folder_contents_return" in param:
        mock_service.list_folder_contents.return_value = param["list_folder_contents_return"]

    return mock_service


@pytest.fixture
def mock_service_account_creds() -> mock.Mock:
    """Mocks service account credentials."""
    return mock.create_autospec(ServiceAccountCredentials)


@pytest.fixture
def real_folder_id(app) -> str:
    """Returns the real folder ID from app config."""
    return app.config.get('DRIVE_BLOG_POSTS_FOLDER_ID')


@pytest.fixture
def test_drive_file_metadata_map():
    """Test Google Drive file metadata map."""
    return {
        "design_principles": {
            "file_id": "1p5jpGiSa1KyXbQrAEJ44NEBP4pgsLqpsdgYUkMgy3Vo",
            "slug": "six-essential-object-oriented-design-principles-from-matthias-nobacks-object-design-style-guide",
        },
        "value_objects": {
            "file_id": "187rlFKQsACliz_ta-niIgK9ZDOwsR9a3YmfrkbX_R1E",
            "slug": "value-objects",
        },
        "value_objects_test": {
            "file_id": "1e8CUUM6S3ZXRXIhoE0oxM_4O5eqH1mr5YyoiWzjpWxI",
            "slug": "value-objects-test",
        },
        "markdown_to_html": {
            "file_id": "1zZM1zY6qmOIuXh2Fb-6oQ3lZ_ETRvEnlnl75Pw3WecE",
            "slug": "markdown-to-html-test",
        },
        "restricted": {
            "file_id": "1LafXfqIfye5PLvwnXpAs0brp8C3qvh81sDI--rG7eSk",
            "slug": "test-restricted-access",
        },
    }


@pytest.fixture
def scopes() -> list[str]:
    """Common Google Drive OAuth2 scopes."""
    return ['https://www.googleapis.com/auth/drive']


@pytest.fixture
def fake_service_account_credentials_json():
    return json.loads("""
    {
        "type": "service_account",
        "project_id": "fake-project",
        "private_key_id": "fake-key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\\n...",
        "client_email": "fake@example.com",
        "client_id": "fake-client-id",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/fake"
    }
    """)


@pytest.fixture(autouse=True)
def clear_drive_service_cache():
    """Fixture to clear the drive service cache before each test."""
    GoogleDriveService._cached_drive_service = None
