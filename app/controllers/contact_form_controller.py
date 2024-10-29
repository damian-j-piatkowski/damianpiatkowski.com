from flask import current_app
from app.exceptions import EmailSendError
from app.services.email_service import send_contact_email
from app.services.sanitization_service import sanitize_contact_form_input
from app.models.forms.contact_form import ContactForm


def handle_contact_form_submission(form_data: dict) -> tuple[bool, str, str]:
    """
    Handles the submission of contact form data, orchestrating the validation,
    sanitization, and email sending process.

    Args:
        form_data (dict): The contact form data containing 'name', 'email',
                          and 'message'.

    Returns:
        tuple[bool, str, str]: A tuple containing:
            - A boolean indicating success (True) or failure (False).
            - A message to be displayed to the user.
            - A message category ('success' or 'danger') for frontend styling.
    """
    # 1. Validate the input using WTForms (or whichever validation method you prefer)
    form = ContactForm(data=form_data)
    if not form.validate():
        # Collect all validation errors and return them as a flash message
        error_messages = '; '.join([f'{field}: {msg[0]}' for field, msg in form.errors.items()])
        return False, f"Validation error(s): {error_messages}", 'danger'

    # 2. Sanitize the input
    sanitized_data = sanitize_contact_form_input(form_data)

    # 3. Extract sanitized data
    name = sanitized_data.get('name')
    email = sanitized_data.get('email')
    message = sanitized_data.get('message')

    # 4. Try to send the email
    try:
        send_contact_email(name, email, message)
        return True, 'Message sent successfully!', 'success'
    except EmailSendError as e:
        # Log the error and return a failure response
        current_app.logger.error(f"Contact form submission failed: {str(e)}")
        return False, 'An error occurred while sending your message.', 'danger'
