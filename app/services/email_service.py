"""Email service for handling contact form submissions.

This module provides functionality to send emails using the configured
Flask-Mail extension. It encapsulates the email preparation and sending
process, allowing the controller to focus on business logic without
directly interacting with email configurations.

Functions:
    - send_contact_email: Prepares and sends an email using form data.

Exceptions:
    - EmailSendError: Raised when an error occurs while sending an email.
"""

from flask import current_app
from flask_mail import Message

from app.exceptions import EmailSendError
from app.extensions import mail


def send_contact_email(name: str, email: str, message: str) -> None:
    """Send an email using the configured email service.

    Args:
        name (str): The sender's name.
        email (str): The sender's email address.
        message (str): The content of the message.

    Raises:
        EmailSendError: If an error occurs while sending the email.
    """
    msg = Message(
        subject="Contact Form Submission",
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[current_app.config['MAIL_RECIPIENT']],
        body=f"Name: {name}\nEmail: {email}\nMessage: {message}"
    )

    try:
        mail.send(msg)
    except Exception as e:
        # Capture the exception and raise the custom EmailSendError
        raise EmailSendError("Failed to send email.", email,
                             error_code=getattr(e, 'code', None)) from e
