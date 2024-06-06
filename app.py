import logging
import os

from flask import Flask

from about_me.routes import about_me_bp
from config import config
from extensions import db, mail
from home.routes import home_bp
from logging_config import configure_logging


def create_app():
    flask_app = Flask(__name__)

    # Determine configuration mode
    flask_app.config.from_object(config[os.getenv('FLASK_ENV', 'default')])

    # Initialize Flask-SQLAlchemy
    db.init_app(flask_app)

    # Initialize Flask-Mail
    mail.init_app(flask_app)

    # Configure logging
    configure_logging(flask_app)

    # Register blueprints
    flask_app.register_blueprint(home_bp)
    flask_app.register_blueprint(about_me_bp)

    app_logger = logging.getLogger(__name__)
    app_logger.info("App created successfully.")

    return flask_app


if __name__ == "__main__":
    app = create_app()
    app.run()
