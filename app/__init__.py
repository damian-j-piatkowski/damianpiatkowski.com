import logging
import os

from flask import Flask
from flask_migrate import Migrate

from app.domain.blog_post import BlogPost
from app.domain.log import Log
from app.extensions import db, mail
from app.orm import start_mappers
from app.routes.about_me import about_me_bp
from app.routes.blog import blog_bp
from app.routes.home import home_bp
from app.routes.resume import resume_bp
from config import config, configure_logging


def create_app():
    flask_app = Flask(__name__)
    flask_app.config.from_object(config[os.getenv('FLASK_ENV', 'default')])

    # Initialize Flask-SQLAlchemy
    db.init_app(flask_app)
    flask_app.logger.info("SQLAlchemy initialized.")

    # Initialize ORM mappers
    start_mappers(flask_app)
    flask_app.logger.info("ORM mappers initialized.")

    # Initialize Flask-Migrate
    Migrate(flask_app, db)
    flask_app.logger.info("Flask-Migrate initialized.")

    # Initialize Flask-Mail
    mail.init_app(flask_app)
    flask_app.logger.info("Flask-Mail initialized.")

    # Configure logging
    configure_logging(flask_app)
    flask_app.logger.info("Logging configured.")

    # Register blueprints
    flask_app.register_blueprint(about_me_bp)
    flask_app.register_blueprint(blog_bp)
    flask_app.register_blueprint(home_bp)
    flask_app.register_blueprint(resume_bp)
    flask_app.logger.info("Blueprints registered.")

    app_logger = logging.getLogger(__name__)
    app_logger.info(f"Database URI: {flask_app.config['SQLALCHEMY_DATABASE_URI']}")
    app_logger.info(f"FLASK_ENV: {flask_app.config['FLASK_ENV']}")
    app_logger.info("App created successfully.")

    return flask_app
