"""Test scenarios for validating the behavior of the blog post upload process from Google Drive.

These scenarios simulate a variety of outcomes during the upload of blog posts via the
`upload_blog_posts_from_drive_controller` controller. Each scenario provides a mock list of file metadata,
a sequence of side effects for the mocked `read_file` method (to simulate different outcomes),
and the expected HTTP status code and response structure.

All scenarios are designed to produce *successful results only* — where all blog post uploads
succeed without any errors — and thus all expect a 201 Created response.

Note: The `created_at` field **is present** in actual responses returned by the API,
but is **intentionally omitted** from the expected results in these test cases to avoid
brittle comparisons. The `created_at` timestamp is tested separately for format and recency.

Scenarios covered:
- one_success
- five_successes
"""

# Scenario 1: One success
one_success = {
    "files": [
        {"id": "valid_file_id", "title": "Valid Blog Post", "slug": "valid-blog-post"},
    ],
    "side_effects": [
        "Categories: Python, Design\n<p>Valid blog post content</p>",
    ],
    "expected_status": 201,
    "expected_response": {
        "success": [
            {
                "title": "Valid Blog Post",
                "slug": "valid-blog-post",
                "html_content": "<p>Valid blog post content</p>",
                "drive_file_id": "valid_file_id",
                "categories": ['Python', 'Design'],
            },
        ],
        "errors": [],
    },
}

# Scenario 2: Five successes
five_successes = {
    "files": [
        {
            "id": f"valid_file_{i}_id",
            "title": f"Valid Blog Post {i}",
            "slug": f"valid-blog-post-{i}"
        }
        for i in range(5)
    ],
    "side_effects": [
        f"Categories: TestCategory{i}, General\n<p>Valid blog post content {i}</p>" for i in range(5)
    ],
    "expected_status": 201,
    "expected_response": {
        "success": [
            {
                "title": f"Valid Blog Post {i}",
                "slug": f"valid-blog-post-{i}",
                "html_content": f"<p>Valid blog post content {i}</p>",
                "drive_file_id": f"valid_file_{i}_id",
                "categories": [f'TestCategory{i}', 'General'],
            }
            for i in range(5)
        ],
        "errors": [],
    },
}

scenarios = [
    one_success,
    five_successes,
]
