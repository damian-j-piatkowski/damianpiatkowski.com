"""Unit tests for the Email Service.

This module contains unit tests for the Email Service, ensuring the correct
behavior of the `send_contact_email` function. These tests cover various
scenarios such as successful email sending, email sending failure due to exceptions,
and edge cases involving empty or missing fields in the contact form.

Test functions:
    - test_send_contact_email_empty_fields: Verifies that missing or empty
      fields are properly handled before attempting to send an email.
    - test_send_contact_email_failure: Verifies behavior when email sending fails
      with an exception.
    - test_send_contact_email_missing_config: Verifies the behavior when configuration
      values for email sending are missing.
    - test_send_contact_email_no_recipient: Verifies the behavior when there is no
      recipient email configured.
    - test_send_contact_email_success: Verifies successful email sending.

Fixtures:
    - app: Provides the Flask application context for testing.
    - mocker: Provides a mocker fixture for mocking objects and methods during tests.

Mocks:
    - Flask-Mail send method: Mocks the `send` function to simulate email sending and
      trigger different error scenarios.
    - current_app config: Mocks the application's config to simulate different email
      configuration setups.
"""

import pytest
from flask import current_app
from flask_mail import Message
from pytest_mock import MockerFixture

from app.exceptions import EmailSendError
from app.services.email_service import send_contact_email


def test_send_contact_email_empty_fields(app, mocker: MockerFixture) -> None:
    """Tests handling of empty or missing fields.

    Verifies that an `EmailSendError` is raised when any of the required fields
    (name, email, or message) are empty or missing.
    """
    with app.app_context():
        mocker.patch('app.extensions.mail.send')  # Mock email send to avoid actual sending

        with pytest.raises(EmailSendError, match="Required fields are missing."):
            send_contact_email('', 'john@example.com', 'This is a test message.')

        with pytest.raises(EmailSendError, match="Required fields are missing."):
            send_contact_email('John Doe', '', 'This is a test message.')

        with pytest.raises(EmailSendError, match="Required fields are missing."):
            send_contact_email('John Doe', 'john@example.com', '')


def test_send_contact_email_failure(app, mocker: MockerFixture) -> None:
    """Tests email sending failure with an exception.

    Ensures that when an exception occurs during the email sending process,
    the service raises a custom `EmailSendError`.
    """
    with app.app_context():
        mocker.patch('app.extensions.mail.send', side_effect=Exception("SMTP error"))

        mocker.patch.object(current_app, 'config', {
            'MAIL_USERNAME': 'test@example.com',
            'MAIL_RECIPIENT': 'recipient@example.com'
        })

        with pytest.raises(EmailSendError, match="Failed to send email."):
            send_contact_email('John Doe', 'john@example.com', 'This is a test message.')


def test_send_contact_email_missing_config(app, mocker: MockerFixture) -> None:
    """Tests behavior when configuration values for email sending are missing.

    Ensures that `EmailSendError` is raised when required configuration
    values like `MAIL_USERNAME` or `MAIL_RECIPIENT` are missing.
    """
    with app.app_context():
        mocker.patch.object(current_app, 'config', {
            'MAIL_USERNAME': None,
            'MAIL_RECIPIENT': None
        })

        with pytest.raises(EmailSendError, match="Email configuration is incomplete."):
            send_contact_email('John Doe', 'john@example.com', 'This is a test message.')


def test_send_contact_email_no_recipient(app, mocker: MockerFixture) -> None:
    """Tests behavior when there is no recipient email configured.

    Ensures that an `EmailSendError` is raised when the recipient email
    address is missing from the configuration.
    """
    with app.app_context():
        mocker.patch.object(current_app, 'config', {
            'MAIL_USERNAME': 'test@example.com',
            'MAIL_RECIPIENT': None
        })

        with pytest.raises(EmailSendError, match="Email configuration is incomplete."):
            send_contact_email('John Doe', 'john@example.com', 'This is a test message.')


def test_send_contact_email_success(app, mocker: MockerFixture) -> None:
    """Tests successful email sending.

    Mocks the Flask-Mail send method and verifies that it is called with
    the correct arguments when sending an email.
    """
    with app.app_context():
        mock_send = mocker.patch('app.extensions.mail.send')

        mocker.patch.object(current_app, 'config', {
            'MAIL_USERNAME': 'test@example.com',
            'MAIL_RECIPIENT': 'recipient@example.com'
        })

        send_contact_email('John Doe', 'john@example.com', 'This is a test message.')

        mock_send.assert_called_once()
        sent_message = mock_send.call_args[0][0]  # The Message object passed to send()
        assert isinstance(sent_message, Message)
        assert sent_message.subject == "Contact Form Submission"
        assert sent_message.sender == 'test@example.com'
        assert sent_message.recipients == ['recipient@example.com']
        assert "This is a test message." in sent_message.body
