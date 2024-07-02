import os
import logging
from logging.handlers import RotatingFileHandler
from app.domain.log import Log
from app.extensions import db


class Config:
    SECRET_KEY = os.environ.get('PORTFOLIO_WEBSITE_FLASK_SECRET')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    # email username
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    # Email application-specific password (Gmail's SMTP server)
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_RECIPIENT = os.environ.get('MAIL_RECIPIENT')

    # Logging configuration
    LOG_FILE = 'app.log'
    LOG_LEVEL = logging.DEBUG
    LOG_TO_DB = False


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost/db_name'
    LOG_LEVEL = logging.INFO


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
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
