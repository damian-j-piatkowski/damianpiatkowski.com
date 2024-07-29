import logging
import os
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler

from app.domain.log import Log
from app.extensions import db

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
    LOG_FILE: str = 'app.log'
    LOG_LEVEL: int = logging.DEBUG
    LOG_TO_DB: bool = False
    MAIL_PORT: int = 587
    MAIL_SERVER: str = 'smtp.gmail.com'
    MAIL_USE_SSL: bool = False
    MAIL_USE_TLS: bool = True
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    @staticmethod
    def get_database_url():
        mysql_user = os.getenv('MYSQL_USER', 'damian_piatkowski')
        mysql_password = os.getenv('MYSQL_PASSWORD', 'dev_password')
        mysql_database = os.getenv('MYSQL_DATABASE', 'test_db')
        mysql_host = os.getenv('MYSQL_HOST', 'db')

        return (f'mysql+pymysql://{mysql_user}:{mysql_password}@'
                f'{mysql_host}/{mysql_database}')

    @staticmethod
    def validate():
        required_vars = [
            'BASE_THUMBNAIL_PATH', 'DOWNLOAD_DIRECTORY',
            'FLASK_ENV', 'MAIL_PASSWORD', 'MAIL_RECIPIENT',
            'MAIL_USERNAME', 'SECRET_KEY', 'MYSQL_USER', 'MYSQL_PASSWORD',
            'MYSQL_DATABASE', 'MYSQL_HOST'
        ]
        missing_vars = [var for var in required_vars if not getattr(Config, var)]
        if missing_vars:
            raise EnvironmentError(
                f"Missing required environment variables: "
                f"{', '.join(missing_vars)}"
            )

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = logging.INFO

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# Set SQLALCHEMY_DATABASE_URI dynamically
Config.SQLALCHEMY_DATABASE_URI = Config.get_database_url()

# Validate environment variables at startup
Config.validate()

def configure_logging(app):
    log_file = app.config.get('LOG_FILE', 'app.log')
    log_level = app.config.get('LOG_LEVEL', logging.DEBUG)
    log_to_db = app.config.get('LOG_TO_DB', False)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    file_handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024, backupCount=10)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    if log_to_db:
        class SQLAlchemyHandler(logging.Handler):
            def emit(self, record):
                log_entry = Log(level=record.levelname, message=record.getMessage())
                db.session.add(log_entry)
                db.session.commit()

        db_handler = SQLAlchemyHandler()
        db_handler.setLevel(log_level)
        db_handler.setFormatter(formatter)
    else:
        db_handler = None

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    if db_handler:
        root_logger.addHandler(db_handler)

    root_logger.propagate = True
