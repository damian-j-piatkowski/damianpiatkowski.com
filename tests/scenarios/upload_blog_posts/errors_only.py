"""Test scenarios for handling various errors during the upload of blog posts from Google Drive."""

from app.exceptions import GoogleDriveFileNotFoundError, GoogleDrivePermissionError

# Scenario 1: One error (File not found)
one_file_not_found = {
    "files": [{"id": "missing_file_id", "title": "Missing Blog Post"}],
    "side_effects": [GoogleDriveFileNotFoundError],
    "expected_status": 400,
    "expected_response": {
        "success": [],
        "errors": [
            {"file_id": "missing_file_id", "error": "File not found on Google Drive"},
        ],
    },
}

# Scenario 2: Three different errors
three_different_errors = {
    "files": [
        {"id": "missing_file_id", "title": "Missing Blog Post"},
        {"id": "permission_denied_file_id", "title": "Permission Denied Blog Post"},
        {"id": "runtime_error_file_id", "title": "Runtime Error Blog Post"},
    ],
    "side_effects": [
        GoogleDriveFileNotFoundError,
        GoogleDrivePermissionError,
        RuntimeError("Error saving blog post"),
    ],
    "expected_status": 500,
    "expected_response": {
        "success": [],
        "errors": [
            {"file_id": "missing_file_id", "error": "File not found on Google Drive"},
            {"file_id": "permission_denied_file_id", "error": "Permission denied on Google Drive"},
            {
                "file_id": "runtime_error_file_id",
                "error": "Unexpected error occurred.",
            },
        ],
    },
}

# Scenario 3: Five same kind of errors (File not found)
five_files_not_found = {
    "files": [
        {"id": f"missing_file_{i}_id", "title": f"Missing Blog Post {i}"} for i in range(5)
    ],
    "side_effects": [GoogleDriveFileNotFoundError] * 5,
    "expected_status": 400,
    "expected_response": {
        "success": [],
        "errors": [
            {"file_id": f"missing_file_{i}_id", "error": "File not found on Google Drive"}
            for i in range(5)
        ],
    },
}

scenarios = [
    one_file_not_found,
    three_different_errors,
    five_files_not_found,
]
