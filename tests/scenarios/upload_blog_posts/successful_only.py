"""Test scenarios for handling successful blog post uploads from Drive."""


# Scenario 1: One success
one_success = {
    "files": [
        {"id": "valid_file_id", "title": "Valid Blog Post"},
    ],
    "side_effects": [
        "Valid blog post content",
    ],
    "expected_status": 201,
    "expected_response": {
        "success": [
            {
                "title": "Valid Blog Post",
                "content": "<p>Valid blog post content</p>",
                "drive_file_id": "valid_file_id",
                "created_at": "2024-12-04T14:18:16+00:00",
            },
        ],
        "errors": [],
    },
}

# Scenario 2: Five successes
five_successes = {
    "files": [
        {"id": f"valid_file_{i}_id", "title": f"Valid Blog Post {i}"}
        for i in range(5)
    ],
    "side_effects": [
        f"Valid blog post content {i}" for i in range(5)
    ],
    "expected_status": 201,
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
        "errors": [],
    },
}

scenarios = [
    one_success,
    five_successes,
]
