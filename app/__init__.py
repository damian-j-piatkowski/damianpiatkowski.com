import logging
import os

from flask import Flask

from app.about_me.routes import about_me_bp
from app.extensions import db, mail
from app.home.routes import home_bp
from app.logging_config import configure_logging
from app.orm import start_mappers
from app.resume.routes import resume_bp
from config import config


def create_app():
    flask_app = Flask(__name__)
    flask_app.config.from_object(config[os.getenv('FLASK_ENV', 'default')])

    # Initialize Flask-SQLAlchemy
    db.init_app(flask_app)

    # Initialize Flask-Mail
    mail.init_app(flask_app)

    # Configure logging
    configure_logging(flask_app)

    # Initialize ORM mappers
    start_mappers()

    # Register blueprints
    flask_app.register_blueprint(home_bp)
    flask_app.register_blueprint(about_me_bp)
    flask_app.register_blueprint(resume_bp)

    app_logger = logging.getLogger(__name__)
    app_logger.info("App created successfully.")

    return flask_app
