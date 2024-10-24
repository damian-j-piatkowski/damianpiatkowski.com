"""Google Drive service module for interacting with Google Drive API.

This module provides functionalities to authenticate with Google Drive,
list folder contents, and read files using the Google Drive API.
"""

import json
import logging
import os
from typing import Callable, List, Dict, Optional

import google.auth.exceptions as google_exceptions
import googleapiclient
from flask import current_app
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app import exceptions

logger = logging.getLogger(__name__)


class GoogleDriveService:
    _cached_drive_service: Optional[
        'googleapiclient.discovery.Resource'] = None  # Class-level cache

    def __init__(
            self,
            drive_service: Optional['googleapiclient.discovery.Resource'] = None,
            authenticate_func: Optional[
                Callable[[str, List[str]], 'googleapiclient.discovery.Resource']] = None
    ) -> None:
        """
        Initializes the GoogleDriveService.

        Args:
            drive_service (googleapiclient.discovery.Resource, optional): A pre-authenticated
                Google Drive service instance. If not provided, the service will be
                authenticated within the class.
            authenticate_func (Callable, optional): A custom function to handle authentication.
                The custom function must accept 'credentials_file_path' and 'scopes' as arguments.
        """
        self.authenticate_func = authenticate_func or self._authenticate_google_drive
        self.drive_service = drive_service or self._get_drive_service()

        # Assert to reassure the type checker that drive_service will always be set
        assert self.drive_service is not None, "Drive service initialization failed."

    def _get_drive_service(self) -> 'googleapiclient.discovery.Resource':
        """Initialize or return the cached Google Drive service instance.

        Returns:
            googleapiclient.discovery.Resource: Authenticated Google Drive service instance.
        """
        if GoogleDriveService._cached_drive_service is None:
            credentials_file_path = os.getenv('GOOGLE_CREDENTIALS_FILE')
            scopes = current_app.config.get('GOOGLE_DRIVE_SCOPES',
                                            ['https://www.googleapis.com/auth/drive'])

            GoogleDriveService._cached_drive_service = self.authenticate_func(
                credentials_file_path, scopes
            )

        return GoogleDriveService._cached_drive_service

    @staticmethod
    def clear_cache() -> None:
        """Clear the cached Google Drive service."""
        GoogleDriveService._cached_drive_service = None

    @staticmethod
    def _authenticate_google_drive(
            credentials_file_path: Optional[str] = None,
            scopes: Optional[List[str]] = None
    ) -> 'googleapiclient.discovery.Resource':
        """Authenticate and return a Google Drive service instance using service account creds.

        Args:
            credentials_file_path (str, optional): Path to the service account credentials file.
            scopes (List[str], optional): List of Google API scopes.

        Returns:
            googleapiclient.discovery.Resource: Authenticated Google Drive service instance.
        """
        try:
            if credentials_file_path:
                logger.info(
                    f"Loading service account credentials from file: {credentials_file_path}")
                creds = ServiceAccountCredentials.from_service_account_file(credentials_file_path)
                creds = creds.with_scopes(scopes)  # Apply scopes
            else:
                logger.error("Credentials file path is missing or invalid.")
                raise exceptions.GoogleDriveAuthenticationError(
                    "Credentials file path is missing or invalid."
                )

            # Return the authenticated Google Drive service
            logger.info("Google Drive service successfully authenticated using service account.")
            return build('drive', 'v3', credentials=creds)

        except FileNotFoundError as e:
            logger.error(f"File not found during authentication: {str(e)}")
            raise exceptions.GoogleDriveAuthenticationError(f"File not found: {str(e)}")

        except google_exceptions.DefaultCredentialsError as e:
            logger.error(f"Error loading credentials: {str(e)}")
            raise exceptions.GoogleDriveAuthenticationError(f"Error loading credentials: {str(e)}")

        except HttpError as e:
            logger.error(f"Google API error during authentication: {str(e)}")
            raise exceptions.GoogleDriveAPIError(
                f"Google API error during authentication: {str(e)}")

    @staticmethod
    def _handle_google_drive_api_errors(error: Exception, context: str = "operation") -> None:
        """Handle Google Drive API errors and raise appropriate custom exceptions."""
        if isinstance(error, HttpError):
            try:
                # Decode and extract the error message from the content
                error_content = json.loads(error.content.decode("utf-8"))
                error_message = error_content.get("error", {}).get("message", "Unknown error")
            except (json.JSONDecodeError, AttributeError):
                error_message = "Unknown error"

            if error.resp.status == 404:
                raise exceptions.GoogleDriveFileNotFoundError(
                    f"Resource not found during {context}."
                )
            elif error.resp.status == 403:
                raise exceptions.GoogleDrivePermissionError(
                    f"Permission denied during {context}."
                )
            else:
                raise exceptions.GoogleDriveAPIError(
                    f"Google Drive API error occurred during {context}: {error_message}"
                )
        else:
            raise exceptions.GoogleDriveAPIError(
                f"Unexpected error occurred during {context}: {error}"
            )

    def list_folder_contents(self, folder_id: str) -> List[Dict[str, str]]:
        """List contents of a Google Drive folder by ID.

        Args:
            folder_id (str): The ID of the Google Drive folder.

        Returns:
            List[Dict[str, str]]: A list of files (each with 'id' and 'name') in the folder.

        Raises:
            Errors are handled by `_handle_google_drive_api_errors`.
        """
        query = f"'{folder_id}' in parents and trashed = false"
        try:
            results = self.drive_service.files().list(  # type: ignore
                q=query,
                fields="files(id, name)"
            ).execute()
            return results.get('files', [])
        except HttpError as error:
            self._handle_google_drive_api_errors(error, context="listing folder contents")

    def read_file(self, file_id: str, mime_type: str = 'text/plain') -> str:
        """Read a Google Drive file by ID.

        Args:
            file_id (str): The ID of the file to read.
            mime_type (str, optional): The MIME type of the file to export (default: 'text/plain').

        Returns:
            str: The content of the file as a string.

        Raises:
            Errors are handled by `_handle_google_drive_api_errors`.
        """
        try:
            file_content = self.drive_service.files().export(fileId=file_id,  # type: ignore
                                                             mimeType=mime_type).execute()
            return file_content.decode('utf-8')
        except HttpError as error:
            self._handle_google_drive_api_errors(error, context="reading file")
