import logging
import re
from logging.handlers import RotatingFileHandler

from sqlalchemy.exc import SQLAlchemyError

from app.domain.log import Log
from app.extensions import db


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
