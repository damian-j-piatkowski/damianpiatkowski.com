"""Test scenarios for validating the behavior of the blog post upload process from Google Drive.

These scenarios simulate a variety of outcomes during the upload of blog posts via the
`upload_blog_posts_from_drive_controller` controller. Each scenario provides a mock list of file metadata,
a sequence of side effects for the mocked `read_file` method (to simulate different outcomes),
and the expected HTTP status code and response structure.

All scenarios are designed to include *unexpected errors*, typically resulting in a 500 Internal Server Error
response. Some scenarios also include successful uploads or expected (non-critical) errors.

Note: The `created_at` field **is present** in actual responses returned by the API,
but is **intentionally omitted** from the expected results in these test cases to avoid
brittle comparisons. The `created_at` timestamp is tested separately for format and recency.

Scenarios covered:
- expected_error_then_unexpected_error
- one_success_then_unexpected_error
- single_file_unexpected_error
- three_successes_then_critical_error
"""

from app.exceptions import GoogleDriveFileNotFoundError

expected_error_then_unexpected_error = {
    "files": [
        {"id": "expected_error_file_id", "title": "Expected Error Blog Post", "slug": "expected-error-blog-post"},
        {"id": "unexpected_error_file_id", "title": "Unexpected Error Blog Post", "slug": "unexpected-error-blog-post"},
    ],
    "side_effects": [
        GoogleDriveFileNotFoundError("Test error: file not found", file_id="expected_error_file_id"),
        Exception("Unexpected error occurred"),
    ],
    "expected_status": 500,
    "expected_response": {
        "success": [],
        "errors": [
            {"file_id": "expected_error_file_id", "error": "File not found on Google Drive"},
            {"file_id": "unexpected_error_file_id",
             "error": "Unexpected error occurred: RuntimeError: Unexpected error occurred."},
        ],
    },
}

one_success_then_unexpected_error = {
    "files": [
        {"id": "success_file_id", "title": "Successful Blog Post", "slug": "successful-blog-post"},
        {"id": "unexpected_error_file_id", "title": "Unexpected Error Blog Post", "slug": "unexpected-error-blog-post"},
    ],
    "side_effects": [
        "Categories: Python, Design\n<p>Expected file content to be a string.</p>",
        Exception("Unexpected error occurred"),
    ],
    "expected_status": 207,
    "expected_response": {
        "success": [
            {
                "title": "Successful Blog Post",
                "html_content": "<p>Expected file content to be a string.</p>",
                "drive_file_id": "success_file_id",
                "slug": "successful-blog-post",
                "categories": ["Python", "Design"],
            }
        ],
        "errors": [
            {"file_id": "unexpected_error_file_id",
             "error": "Unexpected error occurred: RuntimeError: Unexpected error occurred."},
        ],
    },
}

single_file_unexpected_error = {
    "files": [{"id": "unexpected_error_file_id", "title": "Unexpected Error Blog Post",
               "slug": "unexpected-error-blog-post"}],
    "side_effects": [Exception("Unexpected error occurred")],
    "expected_status": 500,
    "expected_response": {
        "success": [],
        "errors": [
            {
                "file_id": "unexpected_error_file_id",
                "error": "Unexpected error occurred: RuntimeError: Unexpected error occurred.",
            }
        ],
    },
}

three_successes_then_critical_error = {
    "files": [
        {"id": "success_file_id_1", "title": "Successful Blog Post 1", "slug": "successful-blog-post-1"},
        {"id": "success_file_id_2", "title": "Successful Blog Post 2", "slug": "successful-blog-post-2"},
        {"id": "success_file_id_3", "title": "Successful Blog Post 3", "slug": "successful-blog-post-3"},
        {"id": "critical_error_file_id", "title": "Critical Error Blog Post", "slug": "critical-error-blog-post"},
        {"id": "unprocessed_file_id", "title": "Unprocessed Blog Post", "slug": "unprocessed-blog-post"},
    ],
    "side_effects": [
        "Categories: Python, Design\n<p>Expected file content to be a string.</p>",
        "Categories: Python, Design\n<p>Expected file content to be a string.</p>",
        "Categories: Python, Design\n<p>Expected file content to be a string.</p>",
        Exception("Critical error occurred"),
    ],
    "expected_status": 207,
    "expected_response": {
        "success": [
            {
                "title": "Successful Blog Post 1",
                "html_content": "<p>Expected file content to be a string.</p>",
                "drive_file_id": "success_file_id_1",
                "slug": "successful-blog-post-1",
                "categories": ["Python", "Design"],
            },
            {
                "title": "Successful Blog Post 2",
                "html_content": "<p>Expected file content to be a string.</p>",
                "drive_file_id": "success_file_id_2",
                "slug": "successful-blog-post-2",
                "categories": ["Python", "Design"],
            },
            {
                "title": "Successful Blog Post 3",
                "html_content": "<p>Expected file content to be a string.</p>",
                "drive_file_id": "success_file_id_3",
                "slug": "successful-blog-post-3",
                "categories": ["Python", "Design"],
            },
        ],
        "errors": [
            {"file_id": "critical_error_file_id",
             "error": "Unexpected error occurred: RuntimeError: Unexpected error occurred."},
        ],
    },
}

scenarios = [
    expected_error_then_unexpected_error,
    one_success_then_unexpected_error,
    single_file_unexpected_error,
    three_successes_then_critical_error,
]
