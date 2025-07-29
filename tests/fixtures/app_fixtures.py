"""Pytest fixtures for testing the Flask application.

This module provides reusable fixtures to support application testing:

Fixtures:
    - app: Creates and configures a Flask app instance using TestingConfig.
    - client: Returns a test client for simulating HTTP requests.
    - runner: Returns a CLI runner for testing Flask CLI commands.
"""


import pytest
from flask import Flask
from flask.testing import FlaskClient, FlaskCliRunner

from app import create_app
from app.config import TestingConfig


@pytest.fixture(scope='session')
def app() -> Flask:
    """Creates a Flask application instance configured for testing."""
    app = create_app(TestingConfig)

    # Inject test-specific config overrides
    app.config.update({
        'MAIL_USERNAME': 'test@example.com',
        'MAIL_RECIPIENT': 'Test Person',
        'DEBUG': True,
        'SECRET_KEY': 'default-secret',
        'SERVER_NAME': 'localhost',
        'APPLICATION_ROOT': '/',
        'PREFERRED_URL_SCHEME': 'http',
        'WTF_CSRF_ENABLED': False,
        'GOOGLE_API_SCOPES': ['https://www.googleapis.com/auth/drive'],
        'TESTING': True,
        'BLOG_IMAGE_BASE_PATH': 'blog-images',
    })

    # 👇 Add a fake static folder path for os.path.exists checks
    app.static_folder = "/fake/static"

    with app.app_context():
        yield app


@pytest.fixture()
def client(app: Flask) -> FlaskClient:
    """Provides a test client for sending HTTP requests to the app."""
    return app.test_client()


@pytest.fixture()
def runner(app: Flask) -> FlaskCliRunner:
    """Provides a CLI runner for invoking app CLI commands."""
    return app.test_cli_runner()