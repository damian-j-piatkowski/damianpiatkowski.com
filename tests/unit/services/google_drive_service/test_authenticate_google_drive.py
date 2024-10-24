"""Unit tests for the _authenticate_google_drive method of the GoogleDriveService class.

This module contains unit tests for the _authenticate_google_drive method, which
handles authentication for the Google Drive API using service account credentials.
The tests cover different scenarios for successful authentication, missing or
invalid credentials files, and error handling.

Tests included:
    - test_authenticate_with_service_account_creds: Verifies successful authentication
      using a service account credentials file.
    - test_authenticate_without_credentials_file: Verifies that an error is raised
      when no credentials file is provided.
    - test_authenticate_with_invalid_credentials_file: Verifies that an error is raised
      when the credentials file cannot be found.
    - test_authenticate_with_google_api_error: Verifies that Google API errors during
      the authentication process are handled properly.

Mocks:
    - Mocks are used for the service account credentials loading and the Google API
      build method to simulate different error conditions and successful responses.
"""

from unittest import mock

import pytest
from googleapiclient.errors import HttpError

from app import exceptions
from app.services.google_drive_service import GoogleDriveService


def test_authenticate_with_service_account_creds(
        mock_env: None,
        mock_service_account_creds: mock.Mock,
        scopes: list[str]
) -> None:
    """Tests authentication using service account credentials.

    Mocks:
        - Service account credentials.
        - google.oauth2.service_account.Credentials.from_service_account_file
        - Google Drive API build function.

    Asserts that the service account credentials are passed correctly to the build method.
    """
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


def test_authenticate_without_credentials_file(
        mock_env: None,
        mock_service_account_creds: mock.Mock,
        scopes: list[str]
) -> None:
    """Tests authentication when no credentials file is provided.

    Asserts that a GoogleDriveAuthenticationError is raised if the credentials file path is missing.
    """
    with pytest.raises(exceptions.GoogleDriveAuthenticationError,
                       match="Credentials file path is missing or invalid."):
        # Call the method with no credentials file, expecting a GoogleDriveAuthenticationError
        GoogleDriveService._authenticate_google_drive(None, scopes)


def test_authenticate_with_invalid_credentials_file(
        mock_env: None,
        mock_service_account_creds: mock.Mock,
        scopes: list[str]
) -> None:
    """Tests authentication with an invalid credentials file.

    Mocks the credentials loader to simulate a FileNotFoundError and asserts that the
    proper exception is raised.
    """
    with mock.patch(
            'google.oauth2.service_account.Credentials.from_service_account_file'
    ) as mock_creds_loader:
        # Simulate an error when trying to load invalid credentials
        mock_creds_loader.side_effect = FileNotFoundError("Credentials file not found")

        with pytest.raises(exceptions.GoogleDriveAuthenticationError,
                           match="File not found: Credentials file not found"):
            # Call the method under test
            GoogleDriveService._authenticate_google_drive('/invalid/path/credentials.json', scopes)


def test_authenticate_with_google_api_error(
        mock_env: None,
        mock_service_account_creds: mock.Mock,
        scopes: list[str]
) -> None:
    """Tests authentication when the Google API raises an HttpError.

    Simulates an HttpError during the Google Drive API build process and asserts that the
    appropriate GoogleDriveAPIError is raised.
    """
    with mock.patch('google.oauth2.service_account.Credentials.from_service_account_file',
                    return_value=mock_service_account_creds), \
            mock.patch('app.services.google_drive_service.build') as mock_build:
        # Simulate an HttpError during build
        mock_build.side_effect = HttpError(mock.Mock(), b"Google API error")

        with pytest.raises(exceptions.GoogleDriveAPIError,
                           match="Google API error during authentication"):
            GoogleDriveService._authenticate_google_drive('/fake/credentials.json', scopes)
