"""Application logging configuration module.

Provides centralized configuration for application loggers, handling console output,
file rotation, and dedicated fallback error logging.
"""

import logging
from logging.handlers import RotatingFileHandler


def configure_logging(app):
    """Configure root and fallback loggers for the Flask application.

    Args:
        app: The Flask application instance containing configuration values.
    """
    log_file = app.config.get('LOG_FILE', '')
    fallback_log_path = app.config.get('FALLBACK_LOG_PATH', '')
    log_level = app.config.get('LOG_LEVEL', logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Set up the console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    # Configure the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Retain pytest's LogCaptureHandler while stripping existing app handlers
    root_logger.handlers = [
        h for h in root_logger.handlers
        if getattr(h, "__module__", "").startswith("_pytest")
    ]
    root_logger.addHandler(console_handler)

    if log_file:  # Only add file handler if a log file is configured
        file_handler = RotatingFileHandler(
            log_file, maxBytes=1024 * 1024, backupCount=10
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    if fallback_log_path:  # Only set up fallback logger if path is provided
        fallback_logger = logging.getLogger('fallback')
        fallback_logger.setLevel(logging.ERROR)  # Log only critical errors
        fallback_file_handler = RotatingFileHandler(
            fallback_log_path, maxBytes=1024 * 1024, backupCount=5
        )
        fallback_file_handler.setFormatter(formatter)

        fallback_logger.handlers = [
            h for h in fallback_logger.handlers
            if getattr(h, "__module__", "").startswith("_pytest")
        ]
        fallback_logger.addHandler(fallback_file_handler)
        root_logger.info("Fallback logger set up.")

    root_logger.propagate = True
