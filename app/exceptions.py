"""Module for custom application-specific exceptions.

This module contains custom exceptions used throughout the application.
These exceptions help encapsulate error handling for various services,
making it easier to catch and handle specific errors in different layers
of the app.

Classes:
    - BlogPostDuplicateError: Raised when attempting to load a duplicate blog post into the db.
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


class BlogPostDuplicateError(Exception):
    """Raised when a duplicate blog post is detected during database operations."""
    def __init__(self, message, title, url):
        """Initializes the BlogPostDuplicateError exception.

        Args:
            message (str): The error message to display.
            title (str): The title of the duplicate blog post.
        """
        self.title = title
        super().__init__(message)


class EmailSendError(Exception):
    """Custom exception for email sending errors with additional context."""

    def __init__(self, message, email, error_code=None):
        """Initializes the EmailSendError exception.

        Args:
            message (str): The error message to display.
            email (str): The email address involved in the error.
            error_code (Optional[int]): An optional error code for further context.
        """
        self.email = email
        self.error_code = error_code
        super().__init__(message)


class GoogleDriveError(Exception):
    """Base exception for Google Drive errors."""
    pass


class GoogleDriveAuthenticationError(GoogleDriveError):
    """Raised when there is an authentication error while interacting with Google Drive."""
    def __init__(self, message, user_email=None):
        """Initializes the GoogleDriveAuthenticationError exception.

        Args:
            message (str): The error message to display.
            user_email (Optional[str]): The email address of the user facing authentication issues.
        """
        self.user_email = user_email
        super().__init__(message)


class GoogleDriveFileNotFoundError(GoogleDriveError):
    """Raised when the requested file is not found in Google Drive."""
    def __init__(self, message, file_id=None):
        """Initializes the GoogleDriveFileNotFoundError exception.

        Args:
            message (str): The error message to display.
            file_id (Optional[str]): The ID of the missing file.
        """
        self.file_id = file_id
        super().__init__(message)


class GoogleDrivePermissionError(GoogleDriveError):
    """Raised when there is a permission error while accessing Google Drive."""
    def __init__(self, message, permission=None):
        """Initializes the GoogleDrivePermissionError exception.

        Args:
            message (str): The error message to display.
            permission (Optional[str]): The permission scope or action that failed.
        """
        self.permission = permission
        super().__init__(message)


class GoogleDriveAPIError(GoogleDriveError):
    """Raised for general API errors that do not fall under other categories."""
    def __init__(self, message, api_method=None, error_code=None):
        """Initializes the GoogleDriveAPIError exception.

        Args:
            message (str): The error message to display.
            api_method (Optional[str]): The API method that caused the error.
            error_code (Optional[int]): An optional error code for further context.
        """
        self.api_method = api_method
        self.error_code = error_code
        super().__init__(message)

