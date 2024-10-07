import os

from flask import current_app
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from googleapiclient.discovery import build

# Module-level cache for the drive service
_cached_drive_service = None


class GoogleDriveService:
    def __init__(self, drive_service):
        self.drive_service = drive_service

    def list_folder_contents(self, folder_id):
        """List contents of a Google Drive folder by ID."""
        query = f"'{folder_id}' in parents and trashed = false"
        results = self.drive_service.files().list(q=query, fields="files(id, name)").execute()
        return results.get('files', [])

    def read_file(self, file_id, mime_type='text/plain'):
        """Read a Google Drive file by ID."""
        file_content = self.drive_service.files().export(fileId=file_id,
                                                         mimeType=mime_type).execute()
        return file_content.decode('utf-8')


def authenticate_google_drive(credentials_file_path=None, token_file_path=None,
                              request=None, scopes=None):
    """Authenticate and return a Google Drive service instance."""
    global _cached_drive_service

    if _cached_drive_service is None:
        creds = None

        # Load credentials from token.json if available
        if token_file_path and os.path.exists(token_file_path):
            creds = Credentials.from_authorized_user_file(token_file_path, scopes)

        # Refresh the token if it's expired
        if creds and creds.expired and creds.refresh_token:
            request = request or Request()
            creds.refresh(request)
            with open(token_file_path, 'w') as token_file:
                token_file.write(creds.to_json())
        else:
            # Use the provided credentials file if no valid token
            creds = ServiceAccountCredentials.from_service_account_file(
                credentials_file_path, scopes=scopes)

        _cached_drive_service = build('drive', 'v3', credentials=creds)

    return _cached_drive_service


def get_google_drive_service():
    """Factory function to instantiate GoogleDriveService."""
    credentials_file_path = os.getenv('GOOGLE_CREDENTIALS_FILE')
    token_file_path = os.getenv('GOOGLE_TOKEN_FILE')
    scopes = current_app.config.get('GOOGLE_DRIVE_SCOPES',
                                    ['https://www.googleapis.com/auth/drive'])

    drive_service = authenticate_google_drive(credentials_file_path, token_file_path, request=None,
                                              scopes=scopes)
    return GoogleDriveService(drive_service)
