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

from app.controllers.admin_controller import get_logs_data


def test_get_logs_data_success(app, session, create_log) -> None:
    """Test successful retrieval of log data."""
    with app.app_context():
        # Create sample logs
        create_log(level='INFO', message='Log entry 1')
        create_log(level='ERROR', message='Log entry 2')
        session.commit()

        # Call the function
        response, status_code = get_logs_data()

        # Adjust expected data to include all fields
        expected_data = [
            {
                'id': 1,
                'level': 'INFO',
                'message': 'Log entry 1',
                'timestamp': response.json[0]['timestamp']  # Match actual timestamp format
            },
            {
                'id': 2,
                'level': 'ERROR',
                'message': 'Log entry 2',
                'timestamp': response.json[1]['timestamp']  # Match actual timestamp format
            }
        ]

        # Assert response data and status code
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
