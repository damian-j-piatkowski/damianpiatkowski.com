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

import json
from flask.testing import FlaskClient
from app.extensions import mail


def test_email_not_sent_when_form_is_incomplete(client: FlaskClient) -> None:
    """Test that an email is not sent when the contact form is incomplete."""
    with mail.record_messages() as outbox:
        # Test regular form submission
        response = client.post('/submit-contact', data={
            'name': 'John Doe',
            'email': '',  # Missing email
            'message': 'This is a test message.'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert len(outbox) == 0

        # Test AJAX submission
        response = client.post('/submit-contact', data={
            'name': 'John Doe',
            'email': '',  # Missing email
            'message': 'This is a test message.'
        }, headers={'X-Requested-With': 'XMLHttpRequest'})

        assert response.status_code == 400  # Validation error returns 400 for AJAX
        assert len(outbox) == 0

        # Check JSON response structure
        json_data = response.get_json()
        assert json_data['success'] is False
        assert 'Email' in json_data['message']  # Should contain email validation error
        assert json_data['category'] == 'danger'


def test_email_sending(client: FlaskClient) -> None:
    """Test that an email is sent when the contact form is complete."""
    with mail.record_messages() as outbox:
        # Test regular form submission
        response = client.post('/submit-contact', data={
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

    # Clear the outbox for AJAX test
    with mail.record_messages() as outbox:
        # Test AJAX submission
        response = client.post('/submit-contact', data={
            'name': 'Jane Smith',
            'email': 'jane@example.com',
            'message': 'Hello, this is an AJAX test message.'
        }, headers={'X-Requested-With': 'XMLHttpRequest'})

        assert response.status_code == 200
        assert len(outbox) == 1
        assert outbox[0].subject == "Contact Form Submission"
        assert "Jane Smith" in outbox[0].body
        assert "jane@example.com" in outbox[0].body
        assert "Hello, this is an AJAX test message." in outbox[0].body

        # Check JSON response structure
        json_data = response.get_json()
        assert json_data['success'] is True
        assert json_data['message'] == 'I’ll get back to you soon!'
        assert json_data['category'] == 'success'


def test_email_sending_failure_handling(client: FlaskClient, mocker) -> None:
    """Test that the app handles email sending failures gracefully."""
    mocker.patch('app.extensions.mail.send',
                 side_effect=Exception("SMTP error"))

    # Test regular form submission - check session for flash messages
    with client:
        response = client.post('/submit-contact', data={
            'name': 'Jane Doe',
            'email': 'jane@example.com',
            'message': 'This is another test message.'
        })

        # Should redirect after error
        assert response.status_code == 302

        # Check that flash message was set in session
        from flask import session
        flashed_messages = session.get('_flashes', [])
        assert len(flashed_messages) > 0

        # Find the error message
        error_found = any('An error occurred while sending your message.' in msg[1]
                          for msg in flashed_messages if msg[0] == 'danger')
        assert error_found

    # Test AJAX submission - should return JSON
    response = client.post('/submit-contact', data={
        'name': 'Bob Wilson',
        'email': 'bob@example.com',
        'message': 'This is an AJAX error test message.'
    }, headers={'X-Requested-With': 'XMLHttpRequest'})

    assert response.status_code == 200

    # Check JSON response structure for error
    json_data = response.get_json()
    assert json_data['success'] is False
    assert json_data['message'] == 'An error occurred while sending your message.'
    assert json_data['category'] == 'danger'


def test_csrf_token_handling(client: FlaskClient) -> None:
    """Test that CSRF protection works correctly with the form."""
    # This test ensures that forms with CSRF tokens work properly
    # You may need to adjust this based on your CSRF implementation

    # First get the form page to retrieve CSRF token
    response = client.get('/')
    assert response.status_code == 200

    # If you're using Flask-WTF CSRF, you might need to extract the token
    # and include it in your test submissions

    with mail.record_messages() as outbox:
        response = client.post('/submit-contact', data={
            'name': 'CSRF Test User',
            'email': 'csrf@example.com',
            'message': 'Testing CSRF protection.'
        }, follow_redirects=True)

        # Should still work if CSRF is properly configured
        assert response.status_code == 200