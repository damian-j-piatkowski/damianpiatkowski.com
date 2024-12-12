"""Test scenarios for handling various outcomes during the upload of blog posts from Drive."""

from app.exceptions import GoogleDriveFileNotFoundError, GoogleDrivePermissionError

# Scenario 1: 1 success, 1 failure
one_success_one_failure = {
    "files": [
        {"id": "valid_file_id", "title": "Valid Blog Post"},
        {"id": "invalid_file_id", "title": "Invalid Blog Post"},
    ],
    "side_effects": ["Expected file content.", GoogleDriveFileNotFoundError],
    "expected_status": 207,
    "expected_response": {
        "success": [
            {
                "title": "Valid Blog Post",
                "content": "<p>Valid blog post content</p>",
                "drive_file_id": "valid_file_id",
                "created_at": "2024-12-04T14:18:16+00:00",
            }
        ],
        "errors": [
            {"file_id": "invalid_file_id", "error": "File not found on Google Drive"},
        ],
    },
}

# Scenario 2: 1 success, 3 failures
one_success_three_failures = {
    "files": [
        {"id": "valid_file_id", "title": "Valid Blog Post"},
        {"id": "missing_file_id", "title": "Missing Blog Post"},
        {"id": "permission_denied_file_id", "title": "Permission Denied Blog Post"},
        {"id": "runtime_error_file_id", "title": "Runtime Error Blog Post"},
    ],
    "side_effects": [
        "Valid blog post content",
        GoogleDriveFileNotFoundError,
        GoogleDrivePermissionError,
        RuntimeError("Error saving blog post"),
    ],
    "expected_status": 207,
    "expected_response": {
        "success": [
            {
                "title": "Valid Blog Post",
                "content": "<p>Valid blog post content</p>",
                "drive_file_id": "valid_file_id",
                "created_at": "2024-12-04T14:18:16+00:00",
            }
        ],
        "errors": [
            {"file_id": "missing_file_id", "error": "File not found on Google Drive"},
            {"file_id": "permission_denied_file_id", "error": "Permission denied"},
            {
                "file_id": "runtime_error_file_id",
                "error": "Error saving blog post: Error saving blog post",
            },
        ],
    },
}

# Scenario 3: 5 successes, 1 failure
five_successes_one_failure = {
    "files": [
                 {"id": f"valid_file_{i}_id", "title": f"Valid Blog Post {i}"} for i in range(5)
             ] + [{"id": "invalid_file_id", "title": "Invalid Blog Post"}],
    "side_effects": [
                        f"Valid blog post content {i}" for i in range(5)
                    ] + [GoogleDriveFileNotFoundError],
    "expected_status": 207,
    "expected_response": {
        "success": [
            {
                "title": f"Valid Blog Post {i}",
                "content": f"<p>Valid blog post content {i}</p>",
                "drive_file_id": f"valid_file_{i}_id",
                "created_at": "2024-12-04T14:18:16+00:00",
            }
            for i in range(5)
        ],
        "errors": [
            {"file_id": "invalid_file_id", "error": "File not found on Google Drive"},
        ],
    },
}

# Scenario 4: 1 success, then the BlogPostDuplicateError
one_success_one_duplicate = {
    "files": [
        {"id": "valid_file_id", "title": "Valid Blog Post"},
        {"id": "valid_file_id", "title": "Valid Blog Post"},
    ],
    "side_effects": ["Expected file content.", "Expected file content."],
    "expected_status": 207,
    "expected_response": {
        "success": [
            {
                "file_id": "valid_file_id",
                "message": (
                    "Blog post successfully processed: "
                    "{'title': 'Valid Blog Post', "
                    "'content': 'Expected file content.', "
                    "'drive_file_id': 'valid_file_id', "
                    "'created_at': '2024-12-04T14:18:16+00:00'}"
                ),
            }
        ],
        "errors": [
            {"file_id": "valid_file_id",
             "error": "Duplicate blog post: drive_file_id 'valid_file_id' already exists."},
        ],
    },
}

scenarios = [
    one_success_one_failure,
    one_success_three_failures,
    five_successes_one_failure,
    one_success_one_duplicate
]
