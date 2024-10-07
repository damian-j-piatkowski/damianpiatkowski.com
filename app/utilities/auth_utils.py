import os
import json
from flask import session

# Utility function to check if a user is authenticated (for session-based web login)
def is_logged_in():
    return session.get('logged_in', False)

# Utility function to verify admin credentials against environment variables
def verify_admin_credentials(username, password):
    admin_user = os.environ.get('ADMIN_USER')
    admin_pass = os.environ.get('ADMIN_PASS')
    return username == admin_user and password == admin_pass

# Utility function to log in a user (for session-based login)
def login_user():
    session['logged_in'] = True

# Utility function to log out a user (for session-based login)
def logout_user():
    session.pop('logged_in', None)

# Utility function to create a temporary credentials.json file from constants
def create_temp_credentials_file():
    """Create a temporary credentials.json file from environment variables."""
    credentials_data = {
        "web": {
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "project_id": os.getenv("GOOGLE_PROJECT_ID"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
        }
    }

    with open('temp_credentials.json', 'w') as credentials_file:
        json.dump(credentials_data, credentials_file)

    return 'temp_credentials.json'
