import logging
from logging.handlers import RotatingFileHandler
from app.models import Log
from app.extensions import db


def configure_logging(app):
    # Retrieve log settings from app configuration
    log_file = app.config.get('LOG_FILE', 'app.log')
    log_level = app.config.get('LOG_LEVEL', logging.DEBUG)
    log_to_db = app.config.get('LOG_TO_DB', False)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Configure file-based logging
    file_handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024,
                                       backupCount=10)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    # Configure database-based logging
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

    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)
    if db_handler:
        root_logger.addHandler(db_handler)

    # Propagate log messages to all handlers
    root_logger.propagate = True
