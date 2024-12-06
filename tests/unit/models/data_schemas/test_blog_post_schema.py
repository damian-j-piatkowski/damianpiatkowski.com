"""Tests for the BlogPostSchema.

This module contains tests for the BlogPostSchema, validating the serialization
and deserialization of blog post data, ensuring that required fields are
present, fields have valid values, and that timestamps are correctly formatted.

Test functions:
- test_blog_post_schema_empty_title: Tests schema when the title is empty.
- test_blog_post_schema_missing_content: Tests schema when content is missing.
- test_blog_post_schema_missing_drive_file_id: Tests schema when the drive file ID is missing.
- test_blog_post_schema_missing_title: Tests schema when the title is missing.
- test_blog_post_schema_timestamp_dumps: Tests schema timestamp serialization.
- test_blog_post_schema_valid: Tests schema with valid blog post data.
"""

from datetime import datetime

import pytest
from marshmallow.exceptions import ValidationError

from app.models.data_schemas.blog_post_schema import BlogPostSchema


def test_blog_post_schema_empty_title(create_blog_post):
    """Tests schema when the title is empty.

    This test ensures that the schema raises a ValidationError when the title
    field is present but contains an empty string.
    """
    schema = BlogPostSchema()
    blog_post = create_blog_post(title="")
    with pytest.raises(ValidationError) as excinfo:
        schema.load(blog_post.__dict__)
    assert "title" in excinfo.value.messages
    assert "Shorter than minimum length 1." in excinfo.value.messages["title"]


def test_blog_post_schema_missing_content(create_blog_post):
    """Tests schema when content is missing.

    This test validates that the schema raises a ValidationError when the
    content field is missing from the input data.
    """
    schema = BlogPostSchema()
    blog_post = create_blog_post(content=None)
    with pytest.raises(ValidationError) as excinfo:
        schema.load(blog_post.__dict__)
    assert "content" in excinfo.value.messages
    assert "Field may not be null." in excinfo.value.messages["content"]


def test_blog_post_schema_missing_drive_file_id(create_blog_post):
    """Tests schema when the drive file ID is missing.

    This test ensures that the schema raises a ValidationError when the drive_file_id
    field is not provided.
    """
    schema = BlogPostSchema()
    blog_post = create_blog_post(drive_file_id=None)
    with pytest.raises(ValidationError) as excinfo:
        schema.load(blog_post.__dict__)
    assert "drive_file_id" in excinfo.value.messages
    assert "Field may not be null." in excinfo.value.messages["drive_file_id"]


def test_blog_post_schema_missing_title(create_blog_post):
    """Tests schema when the title is missing.

    This test checks that the schema raises a ValidationError when the title
    field is missing from the input data.
    """
    schema = BlogPostSchema()
    blog_post = create_blog_post(title=None)
    with pytest.raises(ValidationError) as excinfo:
        schema.load(blog_post.__dict__)
    assert "title" in excinfo.value.messages
    assert "Field may not be null." in excinfo.value.messages["title"]


def test_blog_post_schema_timestamp_dumps(create_blog_post):
    """Tests schema timestamp serialization."""
    schema = BlogPostSchema()
    blog_post = create_blog_post()
    blog_post.created_at = datetime(2023, 7, 2, 12, 0, 0)

    result = schema.dump(blog_post)
    assert "created_at" in result
    assert result["created_at"] == "2023-07-02T12:00:00"


def test_blog_post_schema_valid(create_blog_post):
    """Tests schema with valid blog post data."""
    schema = BlogPostSchema()
    blog_post = create_blog_post()

    # Remove SQLAlchemy-specific fields before validation
    blog_post_dict = schema.dump(blog_post)
    # Remove dump-only fields before loading
    blog_post_dict.pop('id', None)
    blog_post_dict.pop('created_at', None)

    result = schema.load(blog_post_dict)
    assert result == blog_post_dict
