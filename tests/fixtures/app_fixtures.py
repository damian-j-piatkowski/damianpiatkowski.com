"""Fixtures for setting up the Flask application and providing test scripts.

This module includes fixtures that set up the Flask application for testing,
provide a test client for making requests to the application, a CLI runner for
testing command-line interface commands, and a fixture for pushing the app
context with mocked configuration.

Fixtures:
    - app: Creates a Flask application instance for the test session.
    - app_context_with_mocked_config: Pushes the app context and mocks the
        configuration settings for the test session.
    - client: Provides a test client for sending HTTP requests to the app.
    - runner: Provides a CLI runner for testing the app's command-line commands.
"""

import pytest
from flask import Flask, current_app
from flask.testing import FlaskClient, FlaskCliRunner
from pytest_mock import MockerFixture

from app import create_app
from app.config import TestingConfig


@pytest.fixture(scope='session')
def app() -> Flask:
    """Creates a session-wide Flask application for testing.

    Yields:
        Flask: The Flask application instance configured for testing.
    """
    app = create_app(TestingConfig)
    with app.app_context():
        print(f"Running with config: {app.config['SQLALCHEMY_DATABASE_URI']}")
        yield app


@pytest.fixture(scope='function')
def app_context_with_mocked_config(mocker: MockerFixture, client: FlaskClient) -> None:
    """Pushes the app context and mocks common configuration settings.

    This fixture sets up the application context, ensuring it's available for
    testing, and mocks the common configuration settings such as mail username,
    recipient, debug mode, and Google Drive credentials.

    Args:
        mocker (MockerFixture): The pytest-mock fixture to mock objects or methods.
        client (FlaskClient): The Flask test client for making requests.

    Yields:
        None: After setting up the app context and mocking the config, the test
        function proceeds.
    """
    with client.application.app_context():
        mocker.patch.object(
            current_app,
            'config',
            {
                'MAIL_USERNAME': 'test@example.com',
                'MAIL_RECIPIENT': 'Test Person',
                'DEBUG': True,
                'SECRET_KEY': 'default-secret',
                'SERVER_NAME': 'localhost',
                'APPLICATION_ROOT': '/',
                'PREFERRED_URL_SCHEME': 'http',
                'WTF_CSRF_ENABLED': False,
                'GOOGLE_SERVICE_ACCOUNT_JSON': '{"type": "service_account", "project_id": "test"}',
                'GOOGLE_API_SCOPES': ['https://www.googleapis.com/auth/drive'],
            }
        )
        yield



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
