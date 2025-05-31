"""Module for testing email sending functionality.

This module contains tests for the email sending functionality of the app,
ensuring that emails are correctly sent when specific actions are performed,
and that appropriate error handling is in place for various scenarios.

Test Functions:
- test_email_not_sent_when_form_is_incomplete: Tests that an email is not sent
    when the contact form is submitted with incomplete information.
- test_email_sending: Tests the email sending functionality when a contact form
    is submitted, verifying the email's subject, body content, and response
    status.
- test_email_sending_failure_handling: Tests the app's behavior when an
    exception occurs during email sending, ensuring it handles the error
    gracefully and displays an appropriate message.
"""

from flask.testing import FlaskClient
from app.extensions import mail


def test_email_not_sent_when_form_is_incomplete(client: FlaskClient) -> None:
    """Test that an email is not sent when the contact form is incomplete."""
    with mail.record_messages() as outbox:
        response = client.post('/submit_contact', data={
            'name': 'John Doe',
            'email': '',  # Missing email
            'message': 'This is a test message.'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert len(outbox) == 0


def test_email_sending(client: FlaskClient) -> None:
    """Test that an email is sent when the contact form is complete."""
    with mail.record_messages() as outbox:
        response = client.post('/submit_contact', data={
            'name': 'John Doe',
            'email': 'john@example.com',
            'message': 'Hello, this is a test message.'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert len(outbox) == 1
        assert outbox[0].subject == "Contact Form Submission"
        assert "John Doe" in outbox[0].body
        assert "john@example.com" in outbox[0].body
        assert "Hello, this is a test message." in outbox[0].body


def test_email_sending_failure_handling(client: FlaskClient, mocker) -> None:
    """Test that the app handles email sending failures gracefully."""
    mocker.patch('app.extensions.mail.send',
                 side_effect=Exception("SMTP error"))

    response = client.post('/submit_contact', data={
        'name': 'Jane Doe',
        'email': 'jane@example.com',
        'message': 'This is another test message.'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"An error occurred while sending your message." in response.data

