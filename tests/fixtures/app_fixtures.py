"""Fixtures for setting up the Flask application and providing test utilities.

This module includes fixtures that set up the Flask application for testing,
provide a test client for making requests to the application, and a CLI runner
for testing command-line interface commands.

Fixtures:
    - app: Creates a Flask application instance for the test session.
    - client: Provides a test client for sending HTTP requests to the app.
    - runner: Provides a CLI runner for testing the app's command-line commands.
"""

import pytest
from flask import Flask
from flask.testing import FlaskClient, FlaskCliRunner

from app import create_app


@pytest.fixture(scope='session')
def app() -> Flask:
    """Creates a session-wide Flask application for testing.

    Yields:
        Flask: The Flask application instance configured for testing.
    """
    app = create_app('testing')
    with app.app_context():
        print(f"Running with config: {app.config['SQLALCHEMY_DATABASE_URI']}")
        yield app


@pytest.fixture(scope='function')
def client(app: Flask) -> FlaskClient:
    """Provides a test client for sending HTTP requests to the application.

    Args:
        app (Flask): The Flask application instance.

    Returns:
        FlaskClient: A test client for the Flask application.
    """
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app: Flask) -> FlaskCliRunner:
    """Provides a CLI runner for testing command-line interface commands.

    Args:
        app (Flask): The Flask application instance.

    Returns:
        FlaskCliRunner: A CLI runner for invoking the app's CLI commands.
    """
    return app.test_cli_runner()
