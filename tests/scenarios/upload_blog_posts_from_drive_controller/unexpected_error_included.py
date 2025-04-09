"""Test scenarios for handling unexpected errors during the upload of blog posts from Drive."""

from app.exceptions import GoogleDriveFileNotFoundError

single_file_unexpected_error = {
    "files": [{"id": "unexpected_error_file_id", "title": "Unexpected Error Blog Post"}],
    "side_effects": [Exception("Unexpected error occurred")],
    "expected_status": 500,
    "expected_response": {
        "success": [],
        "errors": [
            {
                "file_id": "unexpected_error_file_id",
                "error": "Unexpected error occurred.",
            }
        ],
    },
}

expected_error_then_unexpected_error = {
    "files": [
        {"id": "expected_error_file_id", "title": "Expected Error Blog Post"},
        {"id": "unexpected_error_file_id", "title": "Unexpected Error Blog Post"},
    ],
    "side_effects": [
        GoogleDriveFileNotFoundError,
        Exception("Unexpected error occurred"),
    ],
    "expected_status": 500,
    "expected_response": {
        "success": [],
        "errors": [
            {"file_id": "expected_error_file_id", "error": "File not found on Google Drive"},
            {"file_id": "unexpected_error_file_id", "error": "Unexpected error occurred."},
        ],
    },
}

one_success_then_unexpected_error = {
    "files": [
        {"id": "success_file_id", "title": "Successful Blog Post"},
        {"id": "unexpected_error_file_id", "title": "Unexpected Error Blog Post"},
    ],
    "side_effects": [
        "Expected file content to be a string.",
        Exception("Unexpected error occurred"),
    ],
    "expected_status": 500,
    "expected_response": {
        "success": [
            {
                "file_id": "success_file_id",
                "message": (
                    "Blog post successfully processed: "
                    "{'title': 'Successful Blog Post', "
                    "'content': 'Expected file content to be a string.', "
                    "'drive_file_id': 'success_file_id', "
                    "'created_at': '2024-12-04T14:18:16+00:00'}"
                ),
            }
        ],
        "errors": [
            {"file_id": "unexpected_error_file_id", "error": "Unexpected error occurred."},
        ],
    },
}

three_successes_then_critical_error = {
    "files": [
        {"id": "success_file_id_1", "title": "Successful Blog Post 1"},
        {"id": "success_file_id_2", "title": "Successful Blog Post 2"},
        {"id": "success_file_id_3", "title": "Successful Blog Post 3"},
        {"id": "critical_error_file_id", "title": "Critical Error Blog Post"},
        {"id": "unprocessed_file_id", "title": "Unprocessed Blog Post"},
    ],
    "side_effects": [
        "Expected file content to be a string.",
        "Expected file content to be a string.",
        "Expected file content to be a string.",
        Exception("Critical error occurred"),
    ],
    "expected_status": 500,
    "expected_response": {
        "success": [
            {'file_id': 'success_file_id_1',
             'message': "Blog post successfully processed: {'title': "
                        "'Successful Blog Post 1', 'content': 'Expected file "
                        "content to be a string.', 'drive_file_id': "
                        "'success_file_id_1', 'created_at': "
                        "'2024-12-04T14:18:16+00:00'}"},
            {'file_id': 'success_file_id_2',
             'message': "Blog post successfully processed: {'title': "
                        "'Successful Blog Post 2', 'content': 'Expected file "
                        "content to be a string.', 'drive_file_id': "
                        "'success_file_id_2', 'created_at': "
                        "'2024-12-04T14:18:16+00:00'}"},
            {'file_id': 'success_file_id_3',
             'message': "Blog post successfully processed: {'title': "
                        "'Successful Blog Post 3', 'content': 'Expected file "
                        "content to be a string.', 'drive_file_id': "
                        "'success_file_id_3', 'created_at': "
                        "'2024-12-04T14:18:16+00:00'}"},
        ],
        "errors": [
            {"file_id": "critical_error_file_id", "error": "Unexpected error occurred."},
        ],
    },
}

scenarios = [
    single_file_unexpected_error,
    expected_error_then_unexpected_error,
    one_success_then_unexpected_error,
    three_successes_then_critical_error,
]
