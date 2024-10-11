import os
from typing import Callable

import googleapiclient
from flask import current_app
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.services import exceptions


class GoogleDriveService:
    _cached_drive_service = None  # Class-level cache

    def __init__(
            self,
            drive_service=None,
            authenticate_func: Callable[
                [str, str, list], 'googleapiclient.discovery.Resource'
            ] = None
    ):
        """
        Initializes the GoogleDriveService.

        Args:
            drive_service (googleapiclient.discovery.Resource, optional): A pre-authenticated
                Google Drive service instance. If not provided, the service will be
                authenticated within the class.
            authenticate_func (Callable, optional): A custom function to handle authentication.
                The custom function must accept 'credentials_file_path', 'token_file_path',
                and 'scopes' as arguments.
        """
        self.authenticate_func = authenticate_func or self._authenticate_google_drive
        self.drive_service = drive_service or self._get_drive_service()

    def _get_drive_service(self):
        """Initialize or return the cached Google Drive service instance."""
        if GoogleDriveService._cached_drive_service is None:
            credentials_file_path = os.getenv('GOOGLE_CREDENTIALS_FILE')
            token_file_path = os.getenv('GOOGLE_TOKEN_FILE')
            scopes = current_app.config.get('GOOGLE_DRIVE_SCOPES',
                                            ['https://www.googleapis.com/auth/drive'])

            GoogleDriveService._cached_drive_service = self.authenticate_func(
                credentials_file_path, token_file_path, scopes
            )

        return GoogleDriveService._cached_drive_service

    @staticmethod
    def clear_cache():
        """Clear the cached Google Drive service."""
        GoogleDriveService._cached_drive_service = None

    @staticmethod
    def _authenticate_google_drive(credentials_file_path=None, token_file_path=None,
                                   scopes=None):
        """Authenticate and return a Google Drive service instance."""
        creds = None

        # Load credentials from token.json if available
        if token_file_path and os.path.exists(token_file_path):
            creds = Credentials.from_authorized_user_file(token_file_path, scopes)

        # Refresh the token if it's expired
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(token_file_path, 'w') as token_file:
                token_file.write(creds.to_json())
        else:
            # Load credentials and explicitly apply scopes
            creds = ServiceAccountCredentials.from_service_account_file(credentials_file_path)
            creds = creds.with_scopes(scopes)  # Apply scopes here

        return build('drive', 'v3', credentials=creds)

    def list_folder_contents(self, folder_id):
        """List contents of a Google Drive folder by ID."""
        query = f"'{folder_id}' in parents and trashed = false"
        try:
            results = self.drive_service.files().list(q=query, fields="files(id, name)").execute()
            return results.get('files', [])
        except HttpError as error:
            # Handle specific Google API error and provide a fallback or log the issue
            print(f"An error occurred while listing folder contents: {error}")
            return []

    def read_file(self, file_id, mime_type='text/plain'):
        """Read a Google Drive file by ID."""
        try:
            file_content = self.drive_service.files().export(fileId=file_id,
                                                             mimeType=mime_type).execute()
            return file_content.decode('utf-8')

        except HttpError as error:
            if error.resp.status == 404:
                raise exceptions.GoogleDriveFileNotFoundError(f"File with ID {file_id} not found.")
            elif error.resp.status == 403:
                raise exceptions.GoogleDrivePermissionError(
                    f"Permission denied for file ID {file_id}.")
            else:
                raise exceptions.GoogleDriveAPIError(
                    f"An error occurred while reading the file: {error}")
