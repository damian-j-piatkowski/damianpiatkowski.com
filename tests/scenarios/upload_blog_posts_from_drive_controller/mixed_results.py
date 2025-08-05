"""Test scenarios for validating the behavior of the blog post upload process from Google Drive.

These scenarios simulate a variety of outcomes during the upload of blog posts via the
`upload_blog_posts_from_drive_controller` controller. Each scenario provides a mock list of file metadata,
a sequence of side effects for the mocked `read_file` method (to simulate different outcomes),
and the expected HTTP status code and response structure.

All scenarios are designed to produce *mixed results* — where at least one blog post upload
succeeds and at least one fails — and thus all expect a 207 Multi-Status response.

Note: The `created_at` field **is present** in actual responses returned by the API,
but is **intentionally omitted** from the expected results in these test cases to avoid
brittle comparisons. The `created_at` timestamp is tested separately for format and recency.

Scenarios covered:
- one_failure_then_success
- one_success_one_duplicate
- one_success_one_failure
- one_success_three_failures
- one_success_trimmed_long_content_one_failure
- five_successes_one_failure
"""

from app.exceptions import BlogPostDuplicateError, GoogleDriveFileNotFoundError, GoogleDrivePermissionError

# Scenario 1: 1 failure, then 1 success
one_failure_then_success = {
    "files": [
        {"id": "invalid_file_id", "slug": "invalid-blog-post"},
        {"id": "valid_file_id", "slug": "valid-blog-post"},
    ],
    "side_effects": [
        GoogleDriveFileNotFoundError("Test error: file not found", file_id="invalid_file_id"),
        "\ufeffTitle: Valid Blog Post\nCategories: Python, AI\nMeta Description: metadata.\nKeywords: testing\n\n+++\n\nExpected file content.",
    ],
    "expected_status": 207,
    "expected_response": {
        "success": [
            {
                "title": "Valid Blog Post",
                "html_content": "<p>Expected file content.</p>",
                "drive_file_id": "valid_file_id",
                "slug": "valid-blog-post",
                "categories": ["Python", "AI"],
                "keywords": ['testing'],
                "meta_description": 'metadata.',
                'read_time_minutes': 1,
            }
        ],
        "errors": [
            {
                "file_id": "invalid_file_id",
                "error": "File not found on Google Drive",
            },
        ],
    },
}

# Scenario 2: 1 success, 1 duplicate failure
one_success_one_duplicate = {
    "files": [
        {"id": "valid_file_id", "slug": "valid-blog-post"},
        {"id": "valid_file_id", "slug": "valid-blog-post"},
    ],
    "side_effects": [
        "\ufeffTitle: Valid Blog Post\nCategories: Design\nMeta Description: metadata.\nKeywords: testing\n\n+++\n\nExpected file content.",
        BlogPostDuplicateError(
            "Duplicate blog post: drive_file_id 'valid_file_id' already exists.",
            field_name="drive_file_id",
            field_value="valid_file_id"
        ),
    ],
    "expected_status": 207,
    "expected_response": {
        "success": [
            {
                "title": "Valid Blog Post",
                "html_content": "<p>Expected file content.</p>",
                "drive_file_id": "valid_file_id",
                "slug": "valid-blog-post",
                "categories": ["Design"],
                "keywords": ['testing'],
                "meta_description": 'metadata.',
                'read_time_minutes': 1,
            }
        ],
        "errors": [
            {
                "file_id": "valid_file_id",
                "error": "Duplicate blog post: drive_file_id 'valid_file_id' already exists.",
            },
        ],
    },
}

# Scenario 3: 1 success, 1 failure
one_success_one_failure = {
    "files": [
        {"id": "valid_file_id", "slug": "valid-blog-post"},
        {"id": "invalid_file_id", "slug": "invalid-blog-post"},
    ],
    "side_effects": [
        "\ufeffTitle: Valid Blog Post\nCategories: General\nMeta Description: metadata.\nKeywords: testing\n\n+++\n\nExpected file content.",
        GoogleDriveFileNotFoundError("Test error: file not found", file_id="invalid_file_id"),
    ],
    "expected_status": 207,
    "expected_response": {
        "success": [
            {
                "title": "Valid Blog Post",
                "html_content": "<p>Expected file content.</p>",
                "drive_file_id": "valid_file_id",
                "slug": "valid-blog-post",
                "categories": ["General"],
                "keywords": ['testing'],
                "meta_description": 'metadata.',
                'read_time_minutes': 1,
            }
        ],
        "errors": [
            {"file_id": "invalid_file_id", "error": "File not found on Google Drive"},
        ],
    },
}

# Scenario 4: 1 success, 3 failures
one_success_three_failures = {
    "files": [
        {"id": "valid_file_id", "slug": "valid-blog-post"},
        {"id": "missing_file_id", "slug": "missing-blog-post"},
        {"id": "permission_denied_file_id", "slug": "permission-denied-blog-post"},
        {"id": "runtime_error_file_id", "slug": "runtime-error-blog-post"},
    ],
    "side_effects": [
        "\ufeffTitle: Valid Blog Post\nCategories: Testing\nMeta Description: metadata.\nKeywords: testing\n\n+++\n\nValid blog post content",
        GoogleDriveFileNotFoundError("Test error", file_id="missing_file_id"),
        GoogleDrivePermissionError("Test error"),
        RuntimeError("Error saving blog post"),
    ],
    "expected_status": 207,
    "expected_response": {
        "success": [
            {
                "title": "Valid Blog Post",
                "html_content": "<p>Valid blog post content</p>",
                "drive_file_id": "valid_file_id",
                "slug": "valid-blog-post",
                "categories": ["Testing"],
                "keywords": ['testing'],
                "meta_description": 'metadata.',
                'read_time_minutes': 1,
            }
        ],
        "errors": [
            {"file_id": "missing_file_id", "error": "File not found on Google Drive"},
            {"file_id": "permission_denied_file_id", "error": "Permission denied on Google Drive"},
            {"file_id": "runtime_error_file_id",
             "error": "Unexpected error occurred: RuntimeError: Unexpected error occurred."},
        ],
    },
}

# Scenario 5: 1 success (trimmed content), 1 failure
long_content = (
    "<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
    "Phasellus nec iaculis mauris. <b>Curabitur lacinia</b>, lorem in sodales bibendum, "
    "nibh tortor blandit nulla, non vehicula sem felis quis nunc. "
    "Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae.</p>"
)

one_success_trimmed_long_content_one_failure = {
    "files": [
        {"id": "long_content_file_id", "slug": "trimmed-blog-post"},
        {"id": "invalid_file_id", "slug": "invalid-blog-post"},
    ],
    "side_effects": [
        f"\ufeffTitle: Trimmed Blog Post\nCategories: Writing\nMeta Description: metadata.\nKeywords: testing\n\n+++\n\n{long_content}",
        GoogleDriveFileNotFoundError("Test error", file_id="invalid_file_id"),
    ],
    "expected_status": 207,
    "expected_response": {
        "success": [
            {
                "title": "Trimmed Blog Post",
                "html_content": long_content[:200] + "...",
                "drive_file_id": "long_content_file_id",
                "slug": "trimmed-blog-post",
                "categories": ["Writing"],
                "keywords": ['testing'],
                "meta_description": 'metadata.',
                'read_time_minutes': 1,
            }
        ],
        "errors": [
            {"file_id": "invalid_file_id", "error": "File not found on Google Drive"},
        ],
    },
}

# Scenario 6: 5 successes, 1 failure
five_successes_one_failure = {
    "files": [
        *[
            {"id": f"valid_file_{i}_id", "slug": f"valid-blog-post-{i}"}
            for i in range(5)
        ],
        {"id": "invalid_file_id", "slug": "invalid-blog-post"},
    ],
    "side_effects": [
        *[f"\ufeffTitle: Valid Blog Post {i}\nCategories: Category{i}, Testing\nMeta Description: metadata.\nKeywords: testing\n\n+++\n\nValid blog post content {i}" for i in range(5)],
        GoogleDriveFileNotFoundError("Test error", file_id="invalid_file_id"),
    ],
    "expected_status": 207,
    "expected_response": {
        "success": [
            {
                "title": f"Valid Blog Post {i}",
                "html_content": f"<p>Valid blog post content {i}</p>",
                "drive_file_id": f"valid_file_{i}_id",
                "slug": f"valid-blog-post-{i}",
                "categories": [f"Category{i}", "Testing"],
                "keywords": ['testing'],
                "meta_description": 'metadata.',
                'read_time_minutes': 1,
            }
            for i in range(5)
        ],
        "errors": [
            {"file_id": "invalid_file_id", "error": "File not found on Google Drive"},
        ],
    },
}

# Scenario list ordered by variable name
scenarios = [
    five_successes_one_failure,
    one_failure_then_success,
    one_success_one_duplicate,
    one_success_one_failure,
    one_success_three_failures,
    one_success_trimmed_long_content_one_failure,
]
