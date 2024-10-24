"""Module for custom application-specific exceptions.

This module contains custom exceptions used throughout the application.
These exceptions help encapsulate error handling for various services,
making it easier to catch and handle specific errors in different layers
of the app.

Classes:
    - EmailSendError: Raised when an error occurs while sending an email,
        providing additional context such as the email address and optional
        error code.
    - GoogleDriveError: Base exception for Google Drive errors.
    - GoogleDriveAuthenticationError: Raised when there is an authentication
        error while interacting with Google Drive.
    - GoogleDriveFileNotFoundError: Raised when the requested file is not
        found in Google Drive.
    - GoogleDrivePermissionError: Raised when there is a permission error
        while accessing Google Drive.
    - GoogleDriveAPIError: Raised for general API errors that do not fall under
        other categories when using the Google Drive API.
"""


class EmailSendError(Exception):
    """Custom exception for email sending errors with additional context."""

    def __init__(self, message, email, error_code=None):
        """
        Initialize the EmailSendError exception.

        Args:
            message (str): The error message to display.
            email (str): The email address involved in the error.
            error_code (Optional[int]): An optional error code for further context.
        """
        self.email = email  # Email address that caused the error
        self.error_code = error_code  # Optional error code
        super().__init__(message)


class GoogleDriveError(Exception):
    """Base exception for Google Drive errors."""
    pass


class GoogleDriveAuthenticationError(GoogleDriveError):
    """Raised when there is an authentication error while interacting with Google Drive."""
    pass


class GoogleDriveFileNotFoundError(GoogleDriveError):
    """Raised when the requested file is not found in Google Drive."""
    pass


class GoogleDrivePermissionError(GoogleDriveError):
    """Raised when there is a permission error while accessing Google Drive."""
    pass


class GoogleDriveAPIError(GoogleDriveError):
    """Raised for general API errors that do not fall under other categories."""
    pass
