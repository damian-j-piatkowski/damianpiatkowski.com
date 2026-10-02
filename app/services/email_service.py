"""Email service for handling contact form submissions.

This module provides functionality to send emails using the configured
Flask-Mail extension. It encapsulates the email preparation, validation,
and sending process, allowing the controller to focus on business logic
without directly interacting with email configurations.

Features:
    - Validates required fields (name, email, message) before sending.
    - Ensures email configurations are present (MAIL_USERNAME, MAIL_RECIPIENT).
    - Handles email preparation and sending.

Functions:
    - send_contact_email: Prepares, validates, and sends an email using form data.

Exceptions:
    - EmailSendError: Raised when required fields are missing, email configuration
                      is incomplete, or an error occurs while sending an email.
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
        EmailSendError: If any required fields are missing or if an error occurs while sending.
    """

    # Check for missing or empty required fields
    if not name or not email or not message:
        raise EmailSendError("Required fields are missing.", email)

    # Check if email configuration is missing
    mail_username = current_app.config.get('MAIL_USERNAME')
    mail_recipient = current_app.config.get('MAIL_RECIPIENT')

    if not mail_username or not mail_recipient:
        raise EmailSendError("Email configuration is incomplete.", email)

    msg = Message(
        subject="Contact Form Submission",
        sender=mail_username,
        recipients=[mail_recipient],
        body=f"Name: {name}\nEmail: {email}\nMessage: {message}"
    )

    try:
        mail.send(msg)
    except Exception as e:
        # Capture the exception and raise the custom EmailSendError
        raise EmailSendError("Failed to send email.", email,
                             error_code=getattr(e, 'code', None)) from e


def send_system_health_alert(subject: str, body: str) -> None:
    """Send a system health threshold alert to the configured recipient.

    Args:
        subject: Alert subject line.
        body: Plain-text alert body with metric details.

    Raises:
        EmailSendError: If mail configuration is incomplete or sending fails.
    """
    mail_username = current_app.config.get("MAIL_USERNAME")
    mail_recipient = current_app.config.get("MAIL_RECIPIENT")

    if not mail_username or not mail_recipient:
        raise EmailSendError("Email configuration is incomplete.", mail_recipient or "")

    msg = Message(
        subject=subject,
        sender=mail_username,
        recipients=[mail_recipient],
        body=body,
    )

    try:
        mail.send(msg)
    except Exception as exc:
        raise EmailSendError(
            "Failed to send system health alert.",
            mail_recipient,
            error_code=getattr(exc, "code", None),
        ) from exc