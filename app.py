import logging
import os

from flask import Flask

from config import config
from extensions import db
from home.routes import home_bp
from logging_config import configure_logging


def create_app():
    flask_app = Flask(__name__)

    # Determine configuration mode
    env = os.environ.get('FLASK_ENV', 'development')
    flask_app.config.from_object(config[env])

    # Initialize Flask-SQLAlchemy
    db.init_app(flask_app)

    # Configure logging
    configure_logging(flask_app)

    # Register blueprints
    flask_app.register_blueprint(home_bp)

    app_logger = logging.getLogger(__name__)
    app_logger.info("App created successfully.")

    return flask_app