"""This module handles the logic for submitting contact form data.

It validates the form input, sends the email via the email service, and
handles any exceptions that may occur during the email sending process.
"""

from flask import current_app
from app.exceptions import EmailSendError
from app.services.email_service import send_contact_email


def handle_contact_form_submission(form_data: dict) -> tuple[bool, str, str]:
    """Handles the submission of contact form data.

    This function validates the form data and attempts to send an email using
    the provided information. If the email is sent successfully, it returns
    a success message. If an error occurs, it logs the error and returns an
    appropriate error message.

    Args:
        form_data (dict): The contact form data containing 'name', 'email',
                          and 'message'.

    Returns:
        tuple[bool, str, str]: A tuple containing:
            - A boolean indicating success (True) or failure (False).
            - A message to be displayed to the user.
            - A message category ('success' or 'danger') for frontend styling.
    """
    name = form_data.get('name')
    email = form_data.get('email')
    message = form_data.get('message')

    # Validate form data
    if not name or not email or not message:
        return False, 'All fields are required!', 'danger'

    try:
        send_contact_email(name, email, message)
        return True, 'Message sent successfully!', 'success'
    except EmailSendError as e:
        # Log the custom error message
        current_app.logger.error(f"Contact form submission failed: {str(e)}")
        return False, 'An error occurred while sending your message.', 'danger'
