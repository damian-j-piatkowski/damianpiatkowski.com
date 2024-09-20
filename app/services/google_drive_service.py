# app/services/drive_service.py
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def authenticate_drive_api():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('drive', 'v3', credentials=creds)

def list_files_in_drive():
    service = authenticate_drive_api()
    results = service.files().list(pageSize=10, fields="files(id, name)").execute()
    return results.get('files', [])


def read_file(file_id):
    service = authenticate_drive_api()
    file = service.files().export(fileId=file_id, mimeType='text/plain').execute()
    return file.decode('utf-8')