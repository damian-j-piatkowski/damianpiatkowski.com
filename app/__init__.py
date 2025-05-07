import logging
from typing import Type

from flask import Flask
from flask_migrate import Migrate

from app.domain.blog_post import BlogPost
from app.domain.log import Log
from app.extensions import db, mail
from app.orm import start_mappers
from app.routes.about_me import about_me_bp
from app.routes.admin import admin_bp
from app.routes.blog import blog_bp
from app.routes.home import home_bp
from app.routes.resume import resume_bp
from app.config import BaseConfig
from app.logging_config import configure_logging


def create_app(config_class: Type[BaseConfig]) -> Flask:
    """Creates and configures the Flask application.

        Args:
            config_class: A configuration class (e.g., DevelopmentConfig, ProductionConfig)
                          to use for initializing the app.

        Returns:
            Flask: The configured Flask application instance.
    """
    flask_app = Flask(__name__)

    # Apply the provided configuration
    flask_app.config.from_object(config_class)

    # Initialize Flask-SQLAlchemy
    db.init_app(flask_app)

    # Initialize ORM mappers
    start_mappers(flask_app)

    # Initialize Flask-Migrate
    Migrate(flask_app, db)

    # Initialize Flask-Mail
    mail.init_app(flask_app)

    # Configure logging
    configure_logging(flask_app)

    # Register blueprints
    flask_app.register_blueprint(about_me_bp)
    flask_app.register_blueprint(admin_bp)
    flask_app.register_blueprint(blog_bp)
    flask_app.register_blueprint(home_bp)
    flask_app.register_blueprint(resume_bp)

    with flask_app.app_context():
        app_logger = logging.getLogger(__name__)
        app_logger.info(
            f"Database URI: {flask_app.config['SQLALCHEMY_DATABASE_URI']}")
        app_logger.info(f"FLASK_ENV: {flask_app.config['FLASK_ENV']}")
        app_logger.info(f"Log file path: {flask_app.config['LOG_FILE']}")
        app_logger.info("App created successfully.")

    return flask_app
