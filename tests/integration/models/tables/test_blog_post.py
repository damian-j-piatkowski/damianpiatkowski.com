"""Integration tests for the blog_posts table schema definition.

This module validates database-level constraints, unique key requirements,
JSON array storage capabilities, and automatic timestamp generation for blog post records.
"""

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.tables.blog_post import blog_posts


@pytest.mark.blog
def test_blog_post_creation_and_hydration(session: Session):
    """Verifies that a blog post can be inserted and fetched back with parsed JSON arrays and generated timestamps."""
    stmt = blog_posts.insert().values(
        title="Building High-Performance APIs",
        slug="building-high-performance-apis",
        html_content="<p>Detailed guide on Python backend architecture.</p>",
        drive_file_id="drive_file_12345",
        meta_description="A quick dive into modern API design with Python.",
        keywords=["python", "fastapi", "backend", "architecture"],
        read_time_minutes=8,
        categories=["Engineering", "Python"]
    )
    result = session.execute(stmt)
    session.commit()

    inserted_id = result.inserted_primary_key[0]

    row = session.execute(
        select(blog_posts).where(blog_posts.c.id == inserted_id)
    ).fetchone()

    assert row is not None
    assert row.title == "Building High-Performance APIs"
    assert row.slug == "building-high-performance-apis"
    assert row.keywords == ["python", "fastapi", "backend", "architecture"]
    assert row.categories == ["Engineering", "Python"]
    assert row.created_at is not None
    assert row.updated_at is not None


@pytest.mark.blog
def test_duplicate_blog_post_title_raises_integrity_error(session: Session):
    """Verifies that inserting two blog posts with duplicate titles violates unique constraint rules."""
    payload_1 = {
        "title": "Unique Title",
        "slug": "unique-title-1",
        "html_content": "<p>First post.</p>",
        "drive_file_id": "drive_id_1",
        "meta_description": "First post description.",
        "keywords": [],
        "read_time_minutes": 5,
        "categories": []
    }
    payload_2 = {
        "title": "Unique Title",  # Duplicate title
        "slug": "unique-title-2",
        "html_content": "<p>Second post.</p>",
        "drive_file_id": "drive_id_2",
        "meta_description": "Second post description.",
        "keywords": [],
        "read_time_minutes": 3,
        "categories": []
    }

    session.execute(blog_posts.insert().values(**payload_1))
    session.commit()

    with pytest.raises(IntegrityError):
        session.execute(blog_posts.insert().values(**payload_2))
        session.commit()


@pytest.mark.blog
def test_duplicate_blog_post_slug_raises_integrity_error(session: Session):
    """Verifies that inserting two blog posts with identical URL slugs triggers an IntegrityError."""
    payload_1 = {
        "title": "First Title",
        "slug": "shared-slug",
        "html_content": "<p>First post.</p>",
        "drive_file_id": "drive_id_10",
        "meta_description": "First post description.",
        "keywords": [],
        "read_time_minutes": 4,
        "categories": []
    }
    payload_2 = {
        "title": "Second Title",
        "slug": "shared-slug",  # Duplicate slug
        "html_content": "<p>Second post.</p>",
        "drive_file_id": "drive_id_20",
        "meta_description": "Second post description.",
        "keywords": [],
        "read_time_minutes": 2,
        "categories": []
    }

    session.execute(blog_posts.insert().values(**payload_1))
    session.commit()

    with pytest.raises(IntegrityError):
        session.execute(blog_posts.insert().values(**payload_2))
        session.commit()


@pytest.mark.blog
def test_duplicate_drive_file_id_raises_integrity_error(session: Session):
    """Verifies that duplicate Google Drive file identifiers violate the unique constraint."""
    payload_1 = {
        "title": "Post One",
        "slug": "post-one",
        "html_content": "<p>First post.</p>",
        "drive_file_id": "shared_drive_id",
        "meta_description": "Description one.",
        "keywords": [],
        "read_time_minutes": 5,
        "categories": []
    }
    payload_2 = {
        "title": "Post Two",
        "slug": "post-two",
        "html_content": "<p>Second post.</p>",
        "drive_file_id": "shared_drive_id",  # Duplicate drive_file_id
        "meta_description": "Description two.",
        "keywords": [],
        "read_time_minutes": 5,
        "categories": []
    }

    session.execute(blog_posts.insert().values(**payload_1))
    session.commit()

    with pytest.raises(IntegrityError):
        session.execute(blog_posts.insert().values(**payload_2))
        session.commit()


@pytest.mark.blog
def test_null_required_blog_post_fields_raise_integrity_error(session: Session):
    """Verifies that inserting a blog post omitting mandatory non-nullable fields fails integrity validation."""
    invalid_payload = {
        "title": "Incomplete Post",
        "slug": "incomplete-post",
        "html_content": None,  # Violates NOT NULL
        "drive_file_id": "drive_file_99",
        "meta_description": "Summary",
        "keywords": [],
        "read_time_minutes": 3,
        "categories": []
    }

    with pytest.raises(IntegrityError):
        session.execute(blog_posts.insert().values(**invalid_payload))
        session.commit()