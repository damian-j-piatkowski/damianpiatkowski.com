import os
from dotenv import load_dotenv
import json

load_dotenv()  # Load from .env if not already in environment


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
    GOOGLE_SERVICE_ACCOUNT_JSON = json.loads(os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON'))

    # App-specific
    BASE_THUMBNAIL_PATH = os.environ.get('BASE_THUMBNAIL_PATH', '')
    DOWNLOAD_DIRECTORY = os.environ.get('DOWNLOAD_DIRECTORY', '')
    BLOG_IMAGE_BASE_PATH = 'blog-images'
    PER_PAGE = 9

    # Mail
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_RECIPIENT = os.environ.get('MAIL_RECIPIENT', '')
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'

    # Database
    MYSQL_USER = os.environ.get('MYSQL_USER', '')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', '')
    MYSQL_HOST = os.environ.get('MYSQL_HOST', '')

    @classmethod
    def get_database_url(cls):
        return (f"mysql+pymysql://{cls.MYSQL_USER}:{cls.MYSQL_PASSWORD}@"
                f"{cls.MYSQL_HOST}/{cls.MYSQL_DATABASE}")

    # Logging
    LOG_FILE = os.environ.get('LOG_FILE', '')
    FALLBACK_LOG_PATH = os.environ.get('FALLBACK_LOG_PATH', '')
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_TO_DB = os.environ.get('LOG_TO_DB', 'False').lower() == 'true'

    @classmethod
    def validate(cls):
        missing = []
        for attr in dir(cls):
            if attr.isupper():
                value = getattr(cls, attr)
                if value in (None, '', []):
                    missing.append(attr)
        if missing:
            raise RuntimeError(f"Missing required configuration variables: {', '.join(missing)}")


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = BaseConfig.get_database_url()
    LOG_FILE = os.environ.get('LOG_FILE', '/logs/development/app.log')
    FALLBACK_LOG_PATH = os.environ.get('FALLBACK_LOG_PATH', '/logs/development/fallback.log')
    LOG_TO_DB = os.environ.get('LOG_TO_DB', 'True').lower() == 'true'


class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = BaseConfig.get_database_url()
    LOG_FILE = os.environ.get('LOG_FILE', '/logs/production/app.log')
    FALLBACK_LOG_PATH = os.environ.get('FALLBACK_LOG_PATH', '/logs/production/fallback.log')
    LOG_TO_DB = os.environ.get('LOG_TO_DB', 'True').lower() == 'true'
    BLOG_IMAGE_BASE_PATH = "https://damianpiatkowski-blog.s3.eu-central-1.amazonaws.com"

class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    LOG_FILE = None
    FALLBACK_LOG_PATH = None
    LOG_TO_DB = False
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
