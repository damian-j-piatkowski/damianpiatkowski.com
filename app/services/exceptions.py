class GoogleDriveError(Exception):
    """Base exception for Google Drive errors."""
    pass


class GoogleDriveAuthenticationError(GoogleDriveError):
    """Raised when there is an authentication error."""
    pass


class GoogleDriveFileNotFoundError(GoogleDriveError):
    """Raised when the requested file is not found."""
    pass


class GoogleDrivePermissionError(GoogleDriveError):
    """Raised when there is a permission error."""
    pass


class GoogleDriveAPIError(GoogleDriveError):
    """Raised for general API errors that do not fall under other categories."""
    pass