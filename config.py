import logging
import os
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler
from sqlalchemy.exc import SQLAlchemyError

from app.domain.log import Log
from app.extensions import db
import re


@dataclass
class Config:
    # Environment variables
    BASE_THUMBNAIL_PATH: str = os.getenv('BASE_THUMBNAIL_PATH', '')
    DOWNLOAD_DIRECTORY: str = os.getenv('DOWNLOAD_DIRECTORY', '')
    FLASK_ENV: str = os.getenv('FLASK_ENV', '')
    MAIL_PASSWORD: str = os.getenv('MAIL_PASSWORD', '')
    MAIL_RECIPIENT: str = os.getenv('MAIL_RECIPIENT', '')
    MAIL_USERNAME: str = os.getenv('MAIL_USERNAME', '')
    SECRET_KEY: str = os.getenv('SECRET_KEY', '')
    MYSQL_USER: str = os.getenv('MYSQL_USER', '')
    MYSQL_PASSWORD: str = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DATABASE: str = os.getenv('MYSQL_DATABASE', '')
    MYSQL_HOST: str = os.getenv('MYSQL_HOST', '')

    # Other variables
    DEBUG: bool = False
    LOG_FILE: str = ''
    FALLBACK_LOG_PATH: str = ''
    LOG_LEVEL: int = logging.INFO
    LOG_TO_DB: bool = False
    MAIL_PORT: int = 587
    MAIL_SERVER: str = 'smtp.gmail.com'
    MAIL_USE_SSL: bool = False
    MAIL_USE_TLS: bool = True
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    @staticmethod
    def get_database_url():
        mysql_user = os.getenv('MYSQL_USER', 'default_user')
        mysql_password = os.getenv('MYSQL_PASSWORD', 'default_password')
        mysql_database = os.getenv('MYSQL_DATABASE', 'default_db')
        mysql_host = os.getenv('MYSQL_HOST', 'localhost')

        return (f'mysql+pymysql://{mysql_user}:{mysql_password}@'
                f'{mysql_host}/{mysql_database}')

    def validate(self):
        required_vars = [
            'BASE_THUMBNAIL_PATH', 'DOWNLOAD_DIRECTORY',
            'FLASK_ENV', 'MAIL_PASSWORD', 'MAIL_RECIPIENT',
            'MAIL_USERNAME', 'SECRET_KEY', 'MYSQL_USER', 'MYSQL_PASSWORD',
            'MYSQL_DATABASE', 'MYSQL_HOST'
        ]
        missing_vars = [var for var in required_vars if not getattr(self, var)]
        if missing_vars:
            raise EnvironmentError(
                f"Missing required environment variables: "
                f"{', '.join(missing_vars)}"
            )


class DevelopmentConfig(Config):
    DEBUG = True
    LOG_TO_DB = True
    SQLALCHEMY_DATABASE_URI = Config.get_database_url()
    LOG_FILE = '/logs/development/app.log'
    FALLBACK_LOG_PATH = '/logs/development/fallback.log'


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # In-memory DB for tests
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LOG_TO_DB = False
    LOG_FILE = None  # No log file in testing
    FALLBACK_LOG_PATH = None  # No fallback log in testing


class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = logging.INFO
    LOG_TO_DB = True
    SQLALCHEMY_DATABASE_URI = Config.get_database_url()
    LOG_FILE = '/logs/production/app.log'
    FALLBACK_LOG_PATH = '/logs/production/fallback.log'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# Validate environment variables at startup
config['default']().validate()


def configure_logging(app):
    log_file = app.config.get('LOG_FILE', '')
    fallback_log_path = app.config.get('FALLBACK_LOG_PATH', '')
    log_level = app.config.get('LOG_LEVEL', logging.DEBUG)
    log_to_db = app.config.get('LOG_TO_DB', False)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Set up the console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    # Configure the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()  # Clear existing handlers
    root_logger.addHandler(console_handler)

    if log_file:  # Only add file handler if a log file is configured
        file_handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024,
                                           backupCount=10)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    if fallback_log_path:  # Only set up fallback logger if path is provided
        fallback_logger = logging.getLogger('fallback')
        fallback_logger.setLevel(logging.ERROR)  # Log only critical errors
        fallback_file_handler = RotatingFileHandler(fallback_log_path,
                                                    maxBytes=1024 * 1024,
                                                    backupCount=5)
        fallback_file_handler.setFormatter(formatter)
        fallback_logger.handlers.clear()  # Clear existing handlers
        fallback_logger.addHandler(fallback_file_handler)
        root_logger.info("Fallback logger set up.")

    if log_to_db:
        class SQLAlchemyHandler(logging.Handler):
            ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')

            def emit(self, record):
                try:
                    message = record.getMessage()
                    if ("Running on" in message or
                            "Press CTRL+C to quit" in message):
                        return  # Skip these messages

                    message = self.ansi_escape.sub('', message)

                    log_entry = Log(level=record.levelname, message=message)
                    with app.app_context():
                        db.session.add(log_entry)
                        db.session.commit()
                except SQLAlchemyError as sqle:
                    with app.app_context():
                        db.session.rollback()
                    fallback_logger.error(f"SQLAlchemyError occurred: {sqle}")
                except Exception as e:
                    fallback_logger.error(
                        f"Unexpected error occurred during logging: {e}")

        db_handler = SQLAlchemyHandler()
        db_handler.setLevel(logging.DEBUG)
        db_handler.setFormatter(formatter)
        root_logger.addHandler(db_handler)
        root_logger.info("SQLAlchemyHandler added to root logger.")

    root_logger.propagate = True
