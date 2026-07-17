"""Application configuration registry.

Defines the environment-specific configuration profiles (Development, Production,
and Testing) for the Flask application using a class-based inheritance structure
backed by environment variables.
"""

import json
import os

from dotenv import load_dotenv

# Only try to load .env if not already provided by systemd or env
if not os.getenv("FLASK_ENV"):
    load_dotenv()  # Will load from .env in project root if present


def _build_db_url(user: str, password: str, host: str, database: str) -> str:
    """Helper function to build the SQLAlchemy connection string from clean parameters."""
    return f"mysql+pymysql://{user}:{password}@{host}/{database}"


class BaseConfig:
    # General
    FLASK_ENV = os.environ.get('FLASK_ENV')
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # Admin Panel Google OAuth (frontend-based OAuth login for the admin panel)
    ADMIN_PANEL_ALLOWED_USERS = os.environ.get('ADMIN_PANEL_ALLOWED_USERS', '').split(',')
    ADMIN_PANEL_GOOGLE_CLIENT_ID = os.environ.get('ADMIN_PANEL_GOOGLE_CLIENT_ID')
    ADMIN_PANEL_GOOGLE_CLIENT_SECRET = os.environ.get('ADMIN_PANEL_GOOGLE_CLIENT_SECRET')
    ADMIN_PANEL_GOOGLE_REDIRECT_URI = os.environ.get('ADMIN_PANEL_GOOGLE_REDIRECT_URI')

    # Google Drive API
    DRIVE_BLOG_POSTS_FOLDER_ID = os.environ.get('DRIVE_BLOG_POSTS_FOLDER_ID')
    GOOGLE_DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive']
    GOOGLE_SERVICE_ACCOUNT_JSON = json.loads(os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')) if os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON') else None

    # App-specific
    BLOG_IMAGE_BASE_PATH = os.environ.get('BLOG_IMAGE_BASE_PATH', '')
    DOWNLOAD_DIRECTORY = os.environ.get('DOWNLOAD_DIRECTORY', '')
    PER_PAGE = 9

    # Mail
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_RECIPIENT = os.environ.get('MAIL_RECIPIENT', '')
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'

    # Database Defaults
    MYSQL_USER = os.environ.get('MYSQL_USER', '')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', '')
    MYSQL_HOST = os.environ.get('MYSQL_HOST', '')

    # Logging
    LOG_FILE = os.environ.get('LOG_FILE', '')
    FALLBACK_LOG_PATH = os.environ.get('FALLBACK_LOG_PATH', '')
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

    @classmethod
    def validate(cls):
        """Validates that all strictly required keys for this context are set."""
        missing = []

        # Define fields that are context-dependent and shouldn't crash tests if blank
        ignored_in_testing = {'MYSQL_USER', 'MYSQL_PASSWORD', 'MYSQL_DATABASE', 'GOOGLE_SERVICE_ACCOUNT_JSON'}

        for attr in dir(cls):
            if attr.isupper():
                if getattr(cls, 'TESTING', False) and attr in ignored_in_testing:
                    continue
                value = getattr(cls, attr)
                if value in (None, '', []):
                    missing.append(attr)
        if missing:
            raise RuntimeError(f"Missing required configuration variables: {', '.join(missing)}")


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = _build_db_url(
        BaseConfig.MYSQL_USER,
        BaseConfig.MYSQL_PASSWORD,
        BaseConfig.MYSQL_HOST,
        BaseConfig.MYSQL_DATABASE
    )
    LOG_FILE = os.environ.get('LOG_FILE', '/logs/development/app.log')
    FALLBACK_LOG_PATH = os.environ.get('FALLBACK_LOG_PATH', '/logs/development/fallback.log')


class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = _build_db_url(
        BaseConfig.MYSQL_USER,
        BaseConfig.MYSQL_PASSWORD,
        BaseConfig.MYSQL_HOST,
        BaseConfig.MYSQL_DATABASE
    )
    LOG_FILE = os.environ.get('LOG_FILE', '/logs/production/app.log')
    FALLBACK_LOG_PATH = os.environ.get('FALLBACK_LOG_PATH', '/logs/production/fallback.log')


class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = True

    # 1. Override the credentials on the Testing class namespace
    MYSQL_USER = os.environ.get('MYSQL_USER_TEST', 'damian-test-runner')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD_TEST', '')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE_TEST', 'damian-piatkowski-com-test-db')
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')

    # 2. Build the connection string using the cleanly defined test variables
    SQLALCHEMY_DATABASE_URI = _build_db_url(
        MYSQL_USER,
        MYSQL_PASSWORD,
        MYSQL_HOST,
        MYSQL_DATABASE
    )

    LOG_FILE = None
    FALLBACK_LOG_PATH = None
    DRIVE_BLOG_POSTS_FOLDER_ID = os.environ.get('DRIVE_BLOG_POSTS_FOLDER_ID_TEST')

    # Testing overrides
    SECRET_KEY = os.environ.get('SECRET_KEY', 'test-secret-key')
    ADMIN_PANEL_ALLOWED_USERS = os.environ.get('ADMIN_PANEL_ALLOWED_USERS', 'test@example.com').split(',')
    ADMIN_PANEL_GOOGLE_CLIENT_ID = os.environ.get('ADMIN_PANEL_GOOGLE_CLIENT_ID', 'test-client-id')
    ADMIN_PANEL_GOOGLE_CLIENT_SECRET = os.environ.get('ADMIN_PANEL_GOOGLE_CLIENT_SECRET', 'test-client-secret')
    ADMIN_PANEL_GOOGLE_DISCOVERY_URL = os.environ.get('ADMIN_PANEL_GOOGLE_DISCOVERY_URL',
                                                      'https://accounts.google.com/.well-known/openid-configuration')
    ADMIN_PANEL_GOOGLE_REDIRECT_URI = os.environ.get('ADMIN_PANEL_GOOGLE_REDIRECT_URI',
                                                     'http://localhost:5000/callback')