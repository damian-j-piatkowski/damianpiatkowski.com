"""Tests for the Email Service.

This module contains unit tests for the Email Service, ensuring the correct
behavior of the `send_contact_email` function. These tests cover scenarios
such as successful email sending and handling failures during the email
sending process.

Test functions:
- test_send_contact_email_failure: Tests the behavior when email sending fails
    with an exception.
- test_send_contact_email_success: Tests successful email sending.
"""

import pytest
from flask import current_app
from flask_mail import Message
from pytest_mock import MockerFixture

from app.exceptions import EmailSendError
from app.services.email_service import send_contact_email


def test_send_contact_email_failure(mocker: MockerFixture) -> None:
    """Test email sending failure with an exception.

    This test ensures that when an exception occurs during the email sending
    process, the service raises a custom `EmailSendError`.
    """
    # Mock Flask-Mail's send method to raise an exception
    mocker.patch('app.extensions.mail.send',
                 side_effect=Exception("SMTP error"))

    # Mock current_app config
    mocker.patch.object(current_app, 'config', {
        'MAIL_USERNAME': 'test@example.com',
        'MAIL_RECIPIENT': 'recipient@example.com'
    })

    # Ensure the service raises the custom EmailSendError
    with pytest.raises(EmailSendError) as exc_info:
        send_contact_email('John Doe', 'john@example.com',
                           'This is a test message.')

    # Check if the custom error message matches
    assert str(exc_info.value) == "Failed to send email."
    assert exc_info.value.email == 'john@example.com'


def test_send_contact_email_success(mocker: MockerFixture) -> None:
    """Test successful email sending.

    This test mocks the Flask-Mail send method and verifies that it is called
    with the correct arguments when sending an email.
    """
    # Mock Flask-Mail's send method to ensure it is called
    mock_send = mocker.patch('app.extensions.mail.send')

    # Mock current_app config
    mocker.patch.object(current_app, 'config', {
        'MAIL_USERNAME': 'test@example.com',
        'MAIL_RECIPIENT': 'recipient@example.com'
    })

    # Call the service method
    send_contact_email('John Doe', 'john@example.com',
                       'This is a test message.')

    # Check if Flask-Mail's send was called with the correct arguments
    mock_send.assert_called_once()
    sent_message = mock_send.call_args[0][
        0]  # The Message object passed to send()
    assert isinstance(sent_message, Message)
    assert sent_message.subject == "Contact Form Submission"
    assert sent_message.sender == 'test@example.com'
    assert sent_message.recipients == ['recipient@example.com']
    assert "This is a test message." in sent_message.body
