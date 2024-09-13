"""Tests for the BlogPostSchema.

This module contains tests for the BlogPostSchema, validating the serialization
and deserialization of blog post data, ensuring that required fields are
present, fields have valid values, and that timestamps are correctly formatted.

Test functions:
- test_blog_post_schema_empty_title: Tests schema when the title is empty.
- test_blog_post_schema_missing_content: Tests schema when content is missing.
- test_blog_post_schema_missing_title: Tests schema when the title is missing.
- test_blog_post_schema_timestamp_dumps: Tests schema timestamp serialization.
- test_blog_post_schema_valid: Tests schema with valid blog post data.
"""

from datetime import datetime

import pytest
from marshmallow.exceptions import ValidationError

from app.api_schemas.blog_post_schema import BlogPostSchema


@pytest.fixture
def valid_blog_post_data():
    """Fixture providing valid blog post data."""
    return {
        "title": "Test Blog Post",
        "content": "This is the content of the blog post.",
        "image_small": "path/to/small.jpg",
        "image_medium": "path/to/medium.jpg",
        "image_large": "path/to/large.jpg"
    }


def test_blog_post_schema_empty_title(valid_blog_post_data):
    """Test schema when the title is empty.

    This test ensures that the schema raises a ValidationError when the title
    field is present but contains an empty string.
    """
    schema = BlogPostSchema()
    valid_blog_post_data["title"] = ""
    with pytest.raises(ValidationError) as excinfo:
        schema.load(valid_blog_post_data)
    assert "title" in excinfo.value.messages
    assert "Shorter than minimum length 1." in excinfo.value.messages["title"]


def test_blog_post_schema_missing_content(valid_blog_post_data):
    """Test schema when content is missing.

    This test validates that the schema raises a ValidationError when the
    content field is missing from the input data.
    """
    schema = BlogPostSchema()
    valid_blog_post_data.pop("content")
    with pytest.raises(ValidationError) as excinfo:
        schema.load(valid_blog_post_data)
    assert "content" in excinfo.value.messages
    assert "Missing data for required field." in excinfo.value.messages[
        "content"]


def test_blog_post_schema_missing_title(valid_blog_post_data):
    """Test schema when the title is missing.

    This test checks that the schema raises a ValidationError when the title
    field is missing from the input data.
    """
    schema = BlogPostSchema()
    valid_blog_post_data.pop("title")
    with pytest.raises(ValidationError) as excinfo:
        schema.load(valid_blog_post_data)
    assert "title" in excinfo.value.messages
    assert "Missing data for required field." in excinfo.value.messages["title"]


def test_blog_post_schema_timestamp_dumps(valid_blog_post_data):
    """Test schema timestamp serialization.

    This test verifies that the schema correctly serializes the timestamp
    field to the expected ISO 8601 format when dumping data.
    """
    schema = BlogPostSchema()
    valid_blog_post_data["timestamp"] = datetime(2023, 7, 2, 12, 0, 0)
    result = schema.dump(valid_blog_post_data)
    assert "timestamp" in result
    assert result["timestamp"] == "2023-07-02T12:00:00"


def test_blog_post_schema_valid(valid_blog_post_data):
    """Test schema with valid blog post data.

    This test validates that the schema correctly loads valid data without
    raising any validation errors.
    """
    schema = BlogPostSchema()
    result = schema.load(valid_blog_post_data)
    assert result == valid_blog_post_data
