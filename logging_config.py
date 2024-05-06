import logging
from logging.handlers import RotatingFileHandler
from models import Log
from extensions import db

def configure_logging(app):
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Configure file-based logging
    file_handler = RotatingFileHandler('app.log', maxBytes=1024*1024, backupCount=10)
    file_handler.setFormatter(formatter)

    # Configure database-based logging
    def log_to_database(record):
        log_entry = Log(level=record.levelname, message=record.msg)
        db.session.add(log_entry)
        db.session.commit()

    db_handler = logging.StreamHandler()
    db_handler.setLevel(logging.INFO)
    db_handler.setFormatter(formatter)
    db_handler.set_name('db_handler')
    db_handler.addFilter(lambda record: record.levelname in ['INFO', 'WARNING', 'ERROR', 'CRITICAL'])

    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(db_handler)

    # Propagate log messages to all handlers
    root_logger.propagate = True