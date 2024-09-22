"""
Tests for the Contact Controller.

This module contains tests for the Contact Controller, verifying the behavior of
the `handle_contact_form_submission` function when handling different types of
form submissions, such as valid data, incomplete data, and email sending
failures.

Test functions:
- test_handle_contact_form_submission_email_failure: Tests the controller
    function handling email sending failure.
- test_handle_contact_form_submission_with_incomplete_data: Tests the
    controller function with incomplete form data.
- test_handle_contact_form_submission_with_valid_data: Tests the controller
    function with valid form data.
"""

from typing import Dict

from flask.testing import FlaskClient
from pytest_mock import MockerFixture

from app.controllers.contact_controller import handle_contact_form_submission


def test_handle_contact_form_submission_email_failure(
        mocker: MockerFixture,
        valid_form_data: Dict[str, str],
        client: FlaskClient,
        app_context_with_mocked_config: None  # Using the fixture here
) -> None:
    """Test the controller function handling email sending failure.

    This test mocks both `current_app` and `mail.send` to simulate an email
    sending failure and ensure the function responds correctly.
    """
    # Mock the mail sending function to raise an exception
    mocker.patch('app.extensions.mail.send',
                 side_effect=Exception("SMTP error"))

    success, flash_message, flash_category = handle_contact_form_submission(
        valid_form_data)

    assert success is False
    assert flash_message == 'An error occurred while sending your message.'
    assert flash_category == 'danger'


def test_handle_contact_form_submission_with_incomplete_data(
        incomplete_form_data: Dict[str, str]
) -> None:
    """Test the controller function with incomplete form data.

    This test ensures that when any required form field is missing, the function
    responds with an appropriate failure message and a 'danger' flash category.
    """
    success, flash_message, flash_category = handle_contact_form_submission(
        incomplete_form_data)

    assert success is False
    assert flash_message == 'All fields are required!'
    assert flash_category == 'danger'


def test_handle_contact_form_submission_with_valid_data(
        mocker: MockerFixture,
        valid_form_data: Dict[str, str],
        client: FlaskClient,
        app_context_with_mocked_config: None  # Using the fixture here
) -> None:
    """Test the controller function with valid form data.

    This test mocks both `current_app` and `mail.send` to ensure that the
    function processes valid form data correctly.
    """
    # Mock the mail sending function
    mocker.patch('app.extensions.mail.send')

    success, flash_message, flash_category = handle_contact_form_submission(
        valid_form_data)

    assert success is True
    assert flash_message == 'Message sent successfully!'
    assert flash_category == 'success'
