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
    _cached_drive_service: Optional['googleapiclient.discovery.Resource'] = None

    def __init__(
            self,
            drive_service: Optional['googleapiclient.discovery.Resource'] = None,
            authenticate_func: Optional[
                Callable[[Dict, List[str]], 'googleapiclient.discovery.Resource']
            ] = None
    ) -> None:
        """
        Initializes the GoogleDriveService.

        Args:
            drive_service (googleapiclient.discovery.Resource, optional): Pre-authenticated service.
            authenticate_func (Callable, optional): Custom function for authentication.
                Accepts service_account_info (dict) and scopes (list) as arguments.
        """
        self.authenticate_func = authenticate_func or self._authenticate_google_drive
        self.drive_service = drive_service or self._get_drive_service()
        assert self.drive_service is not None, "Drive service initialization failed."

    def _get_drive_service(self) -> 'googleapiclient.discovery.Resource':
        """Initialize or return the cached Google Drive service."""
        if GoogleDriveService._cached_drive_service is None:
            service_account_info = current_app.config.get('GOOGLE_SERVICE_ACCOUNT_JSON')
            if not service_account_info:
                logger.error("Config value GOOGLE_SERVICE_ACCOUNT_JSON is missing.")
                raise exceptions.GoogleDriveAuthenticationError(
                    "GOOGLE_SERVICE_ACCOUNT_JSON config value is missing."
                )

            if not isinstance(service_account_info, dict):
                logger.error("GOOGLE_SERVICE_ACCOUNT_JSON must be a dictionary.")
                raise exceptions.GoogleDriveAuthenticationError(
                    "GOOGLE_SERVICE_ACCOUNT_JSON must be a dictionary."
                )

            scopes = current_app.config.get(
                'GOOGLE_DRIVE_SCOPES',
                ['https://www.googleapis.com/auth/drive']
            )

            GoogleDriveService._cached_drive_service = self.authenticate_func(
                service_account_info, scopes
            )

        return GoogleDriveService._cached_drive_service

    @staticmethod
    def clear_cache() -> None:
        """Clear the cached Google Drive service."""
        GoogleDriveService._cached_drive_service = None

    @staticmethod
    def _authenticate_google_drive(
            service_account_info: Dict,
            scopes: Optional[List[str]] = None
    ) -> 'googleapiclient.discovery.Resource':
        """Authenticate using service account credentials info (dict)."""
        try:
            if not service_account_info:
                raise exceptions.GoogleDriveAuthenticationError("Service account info is missing or invalid.")

            creds = ServiceAccountCredentials.from_service_account_info(service_account_info)
            creds = creds.with_scopes(scopes)
            logger.info("Google Drive service successfully authenticated using service account.")
            return build('drive', 'v3', credentials=creds)

        except google_exceptions.DefaultCredentialsError as e:
            logger.error(f"Error loading credentials: {str(e)}")
            raise exceptions.GoogleDriveAuthenticationError(f"Error loading credentials: {str(e)}")

        except ValueError as e:
            logger.error(f"Invalid credentials: {str(e)}")
            raise exceptions.GoogleDriveAuthenticationError(f"Invalid credentials: {str(e)}")

        except HttpError as e:
            logger.error(f"Google API error during authentication: {str(e)}")
            raise exceptions.GoogleDriveAPIError(f"Google API error during authentication: {str(e)}")

        except exceptions.GoogleDriveAuthenticationError:
            # Let our own raised AuthenticationError pass through without wrapping again
            raise

        except Exception as e:
            logger.error(f"Unexpected error during authentication: {str(e)}")
            raise exceptions.GoogleDriveAuthenticationError(f"Unexpected error: {str(e)}")

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

            status_code = getattr(error.resp, "status", None)

            logger.error(f"Google API error during {context}: {error_message} (status {status_code})")

            if status_code == 404:
                raise exceptions.GoogleDriveFileNotFoundError(
                    f"Resource not found during {context}."
                )
            elif status_code == 403:
                raise exceptions.GoogleDrivePermissionError(
                    f"Permission denied during {context}."
                )
            else:
                raise exceptions.GoogleDriveAPIError(
                    f"Google Drive API error occurred during {context}: {error_message}"
                )
        else:
            logger.error(f"Unexpected error during {context}: {str(error)}")
            raise exceptions.GoogleDriveAPIError(
                f"Unexpected error during {context}: {str(error)}"
            )

    def list_folder_contents(self, folder_id: str) -> List[Dict[str, str]]:
        query = f"'{folder_id}' in parents and trashed = false"
        try:
            results = self.drive_service.files().list(  # type: ignore
                q=query,
                fields="files(id, name)"
            ).execute()
            return results.get('files') or []
        except HttpError as error:
            self._handle_google_drive_api_errors(error, context="listing folder contents")
            return []

    def read_file(self, file_id: str, mime_type: str = 'text/plain') -> str:
        try:
            file_content = self.drive_service.files().export(fileId=file_id,  # type: ignore
                                                             mimeType=mime_type).execute()
            if file_content is None:
                return ""
            return file_content.decode('utf-8')
        except HttpError as error:
            self._handle_google_drive_api_errors(error, context="reading file")
            return ""
