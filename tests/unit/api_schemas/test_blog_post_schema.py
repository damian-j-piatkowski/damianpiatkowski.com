from datetime import datetime

import pytest
from marshmallow.exceptions import ValidationError
from app.api_schemas.blog_post_schema import BlogPostSchema


@pytest.fixture
def valid_blog_post_data():
    return {
        "title": "Test Blog Post",
        "content": "This is the content of the blog post.",
        "image_small": "path/to/small.jpg",
        "image_medium": "path/to/medium.jpg",
        "image_large": "path/to/large.jpg"
    }


def test_blog_post_schema_valid(valid_blog_post_data):
    schema = BlogPostSchema()
    result = schema.load(valid_blog_post_data)
    assert result == valid_blog_post_data


def test_blog_post_schema_missing_title(valid_blog_post_data):
    schema = BlogPostSchema()
    valid_blog_post_data.pop("title")
    with pytest.raises(ValidationError) as excinfo:
        schema.load(valid_blog_post_data)
    assert "title" in excinfo.value.messages
    assert "Missing data for required field." in excinfo.value.messages["title"]


def test_blog_post_schema_empty_title(valid_blog_post_data):
    schema = BlogPostSchema()
    valid_blog_post_data["title"] = ""
    with pytest.raises(ValidationError) as excinfo:
        schema.load(valid_blog_post_data)
    assert "title" in excinfo.value.messages
    assert "Shorter than minimum length 1." in excinfo.value.messages["title"]


def test_blog_post_schema_missing_content(valid_blog_post_data):
    schema = BlogPostSchema()
    valid_blog_post_data.pop("content")
    with pytest.raises(ValidationError) as excinfo:
        schema.load(valid_blog_post_data)
    assert "content" in excinfo.value.messages
    assert "Missing data for required field." in excinfo.value.messages[
        "content"]


def test_blog_post_schema_timestamp_dumps(valid_blog_post_data):
    schema = BlogPostSchema()
    valid_blog_post_data["timestamp"] = datetime(2023, 7, 2, 12, 0, 0)
    result = schema.dump(valid_blog_post_data)
    assert "timestamp" in result
    assert result["timestamp"] == "2023-07-02T12:00:00"
