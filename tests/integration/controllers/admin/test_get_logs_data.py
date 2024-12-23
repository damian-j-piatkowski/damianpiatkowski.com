"""Integration tests for the get_logs_data controller function.

This module contains integration tests for the get_logs_data function,
focusing on retrieving log data and handling various scenarios, such as
successful retrieval, absence of logs, and runtime errors.

Tests included:
    - test_get_logs_data_success: Verifies that logs are retrieved successfully.
    - test_get_logs_data_no_logs_found: Ensures correct behavior when no logs exist.
    - test_get_logs_data_runtime_error: Tests handling of a runtime error when retrieving logs.

Fixtures:
    - app: Provides the Flask application context for the tests.
    - create_log: Fixture to create log entries in the database.
    - mocker: Provides mocking utilities for external dependencies.
    - session: Provides a session object for database interactions.
"""

from datetime import datetime, timezone

from freezegun import freeze_time

from app.controllers.admin_controller import get_logs_data
from app.models.data_schemas.log_schema import LogSchema


@freeze_time("2024-12-04 14:18:16")
def test_get_logs_data_success(app, session, create_log):
    """Test successful retrieval of log data."""
    with app.app_context():
        first_log_id = create_log(level='INFO', message='Log entry 1').log_id
        second_log_id = create_log(level='ERROR', message='Log entry 2').log_id
        session.commit()

        response, status_code = get_logs_data()

        expected_data = [
            {
                'log_id': first_log_id,
                'level': 'INFO',
                'message': 'Log entry 1',
                'timestamp': "2024-12-04T14:18:16+00:00"
            },
            {
                'log_id': second_log_id,
                'level': 'ERROR',
                'message': 'Log entry 2',
                'timestamp': "2024-12-04T14:18:16+00:00"
            }
        ]

        assert status_code == 200
        assert response.json == expected_data


def test_get_logs_data_no_logs_found(app, session) -> None:
    """Test when there are no logs in the database."""
    with app.app_context():
        # Call the function
        response, status_code = get_logs_data()

        # Assert response data and status code
        assert status_code == 404
        assert response.json == {'message': 'No logs found'}


def test_get_logs_data_runtime_error(app, mocker) -> None:
    """Test the case where a runtime error occurs while fetching logs."""
    with app.app_context():
        # Mock fetch_all_logs to raise a RuntimeError
        mocker.patch('app.services.log_service.fetch_all_logs',
                     side_effect=RuntimeError("Database error"))

        # Call the function
        response, status_code = get_logs_data()

        # Assert response data and status code
        assert status_code == 500
        assert 'Failed to retrieve log data' in response.json['error']
