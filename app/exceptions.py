"""Module for custom application-specific exceptions.

This module contains custom exceptions used throughout the application.
These exceptions help encapsulate error handling for various services,
making it easier to catch and handle specific errors in different layers
of the app.

Classes:
    - EmailSendError: Raised when an error occurs while sending an email,
        providing additional context such as the email address and optional
        error code.
"""


class EmailSendError(Exception):
    """Custom exception for email sending errors with additional context."""

    def __init__(self, message, email, error_code=None):
        """
        Initialize the EmailSendError exception.

        Args:
            message (str): The error message to display.
            email (str): The email address involved in the error.
            error_code (Optional[int]): An optional error code for further
                context.
        """
        self.email = email  # Email address that caused the error
        self.error_code = error_code  # Optional error code
        super().__init__(message)
