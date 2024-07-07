import os
import logging
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler
from app.domain.log import Log
from app.extensions import db


@dataclass
class Config:
    SECRET_KEY: str = os.getenv('PORTFOLIO_WEBSITE_FLASK_SECRET')
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_DATABASE_URI: str = ''
    MAIL_SERVER: str = 'smtp.gmail.com'
    MAIL_PORT: int = 587
    MAIL_USE_TLS: bool = True
    MAIL_USE_SSL: bool = False
    # email username
    MAIL_USERNAME: str = os.getenv('MAIL_USERNAME')
    # Email application-specific password (Gmail's SMTP)
    MAIL_PASSWORD: str = os.getenv('MAIL_PASSWORD')
    MAIL_RECIPIENT: str = os.getenv('MAIL_RECIPIENT')
    LOG_FILE: str = 'app.log'
    LOG_LEVEL: int = logging.DEBUG
    LOG_TO_DB: bool = False


class TestConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost/db_name'
    LOG_LEVEL = logging.INFO


config = {
    'development': TestConfig,
    'production': ProductionConfig,
    'default': TestConfig
}


def configure_logging(app):
    log_file = app.config.get('LOG_FILE', 'app.log')
    log_level = app.config.get('LOG_LEVEL', logging.DEBUG)
    log_to_db = app.config.get('LOG_TO_DB', False)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    file_handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024,
                                       backupCount=10)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    if log_to_db:
        class SQLAlchemyHandler(logging.Handler):
            def emit(self, record):
                log_entry = Log(level=record.levelname,
                                message=record.getMessage())
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
    if db_handler:
        root_logger.addHandler(db_handler)

    root_logger.propagate = True
