import logging
from logging.handlers import RotatingFileHandler


def configure_logging(app):
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

    root_logger.propagate = True