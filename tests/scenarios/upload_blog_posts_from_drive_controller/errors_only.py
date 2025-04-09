"""Test scenarios for handling error-only outcomes during blog post uploads from Google Drive.

These scenarios are used to verify behavior when all attempted blog post uploads result in errors.
Each scenario includes a list of input file metadata, a sequence of side effects representing
exceptions raised during file processing, and the expected HTTP status code and response.

Scenarios covered:
- A single failure due to a missing file.
- Multiple identical errors (e.g., all files missing).
- Multiple distinct errors (e.g., file not found, permission denied, runtime failure).

All scenarios are expected to return either a 400 (client-side issue) or 500 (server-side issue)
status depending on the nature of the errors.
"""

from app.exceptions import GoogleDriveFileNotFoundError, GoogleDrivePermissionError

# Scenario 1: Five identical errors (File not found)
five_files_not_found = {
    "files": [
        {
            "id": f"missing_file_{i}_id",
            "title": f"Missing Blog Post {i}",
            "slug": f"missing-blog-post-{i}",
        }
        for i in range(5)
    ],
    "side_effects": [
        GoogleDriveFileNotFoundError("Test error", file_id=f"missing_file_{i}_id")
        for i in range(5)
    ],
    "expected_status": 400,
    "expected_response": {
        "success": [],
        "errors": [
            {"file_id": f"missing_file_{i}_id", "error": "File not found on Google Drive"}
            for i in range(5)
        ],
    },
}

# Scenario 2: One error (File not found)
one_file_not_found = {
    "files": [{"id": "missing_file_id", "title": "Missing Blog Post", "slug": "missing-blog-post"}],
    "side_effects": [GoogleDriveFileNotFoundError("Test error: file not found", file_id="missing_file_id")],
    "expected_status": 400,
    "expected_response": {
        "success": [],
        "errors": [
            {"file_id": "missing_file_id", "error": "File not found on Google Drive"},
        ],
    },
}

# Scenario 3: Three different errors
three_different_errors = {
    "files": [
        {"id": "missing_file_id", "title": "Missing Blog Post", "slug": "missing-blog-post"},
        {"id": "permission_denied_file_id", "title": "Permission Denied Blog Post",
         "slug": "permission-denied-blog-post"},
        {"id": "runtime_error_file_id", "title": "Runtime Error Blog Post", "slug": "runtime-error-blog-post"},
    ],
    "side_effects": [
        GoogleDriveFileNotFoundError("Test error: file not found", file_id="missing_file_id"),
        GoogleDrivePermissionError("Test error"),
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
                "error": "Unexpected error occurred: RuntimeError: Unexpected error occurred.",
            },
        ],
    },
}

scenarios = [
    five_files_not_found,
    one_file_not_found,
    three_different_errors,
]
