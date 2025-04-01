"""Tests for the BlogPostSchema.

This module contains tests for the BlogPostSchema, validating the serialization
and deserialization of blog post data, ensuring that required fields are
present, fields have valid values, and that timestamps are correctly formatted.

Test functions:
- test_blog_post_schema_empty_title: Tests schema when the title is empty.
- test_blog_post_schema_empty_slug: Tests schema when the slug is empty.
- test_blog_post_schema_missing_content: Tests schema when content is missing.
- test_blog_post_schema_missing_drive_file_id: Tests schema when the drive file ID is missing.
- test_blog_post_schema_missing_slug: Tests schema when the slug is missing.
- test_blog_post_schema_missing_title: Tests schema when the title is missing.
- test_blog_post_schema_timestamp_dumps: Tests schema timestamp serialization.
- test_blog_post_schema_valid: Tests schema with valid blog post data.
"""

from datetime import datetime

import pytest
from freezegun import freeze_time
from marshmallow.exceptions import ValidationError

from app.models.data_schemas.blog_post_schema import BlogPostSchema


def test_blog_post_schema_empty_slug():
    """Tests schema when the slug is empty."""
    schema = BlogPostSchema()
    blog_post_data = {
        "title": "Valid Title",
        "slug": "",
        "content": "Some content",
        "drive_file_id": "some-drive-id",
    }
    with pytest.raises(ValidationError) as excinfo:
        schema.load(blog_post_data)
    assert "slug" in excinfo.value.messages
    assert "Shorter than minimum length 1." in excinfo.value.messages["slug"]


def test_blog_post_schema_empty_title():
    """Tests schema when the title is empty."""
    schema = BlogPostSchema()
    blog_post_data = {
        "title": "",
        "slug": "valid-slug",
        "content": "Some content",
        "drive_file_id": "some-drive-id",
    }
    with pytest.raises(ValidationError) as excinfo:
        schema.load(blog_post_data)
    assert "title" in excinfo.value.messages
    assert "Shorter than minimum length 1." in excinfo.value.messages["title"]


def test_blog_post_schema_missing_content():
    """Tests schema when content is missing."""
    schema = BlogPostSchema()
    blog_post_data = {
        "title": "Valid Title",
        "slug": "valid-slug",
        "drive_file_id": "some-drive-id",
    }
    with pytest.raises(ValidationError) as excinfo:
        schema.load(blog_post_data)
    assert "content" in excinfo.value.messages
    assert "Missing data for required field." in excinfo.value.messages["content"]


def test_blog_post_schema_missing_drive_file_id():
    """Tests schema when the drive file ID is missing."""
    schema = BlogPostSchema()
    blog_post_data = {
        "title": "Valid Title",
        "slug": "valid-slug",
        "content": "Some content",
    }
    with pytest.raises(ValidationError) as excinfo:
        schema.load(blog_post_data)
    assert "drive_file_id" in excinfo.value.messages
    assert "Missing data for required field." in excinfo.value.messages["drive_file_id"]


def test_blog_post_schema_missing_slug():
    """Tests schema when the slug is missing."""
    schema = BlogPostSchema()
    blog_post_data = {
        "title": "Valid Title",
        "content": "Some content",
        "drive_file_id": "some-drive-id",
    }
    with pytest.raises(ValidationError) as excinfo:
        schema.load(blog_post_data)
    assert "slug" in excinfo.value.messages
    assert "Missing data for required field." in excinfo.value.messages["slug"]


def test_blog_post_schema_missing_title():
    """Tests schema when the title is missing."""
    schema = BlogPostSchema()
    blog_post_data = {
        "slug": "valid-slug",
        "content": "Some content",
        "drive_file_id": "some-drive-id",
    }
    with pytest.raises(ValidationError) as excinfo:
        schema.load(blog_post_data)
    assert "title" in excinfo.value.messages
    assert "Missing data for required field." in excinfo.value.messages["title"]


def test_blog_post_schema_timestamp_dumps(create_blog_post):
    """Tests schema timestamp serialization."""
    schema = BlogPostSchema()
    blog_post = create_blog_post()
    blog_post.created_at = datetime(2023, 7, 2, 12, 0, 0)

    result = schema.dump(blog_post)
    assert "created_at" in result
    assert result["created_at"] == "2023-07-02 12:00:00"  # Updated format


@freeze_time("2024-12-04 14:18:16")
def test_blog_post_schema_valid(create_blog_post):
    """Tests schema with valid blog post data."""
    schema = BlogPostSchema()
    blog_post = create_blog_post()

    # Serialize to dict
    blog_post_dict = schema.dump(blog_post)
    blog_post_dict.pop("id", None)

    # Deserialize back
    result = schema.load(blog_post_dict)

    # Ensure `created_at` is correctly formatted
    assert blog_post_dict["created_at"] == "2024-12-04 14:18:16"  # Updated format
    assert result["created_at"].strftime("%Y-%m-%d %H:%M:%S") == "2024-12-04 14:18:16"
