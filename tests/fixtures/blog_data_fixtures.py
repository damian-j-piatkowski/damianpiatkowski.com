"""Fixtures for seeding blog post data in tests.

This module provides reusable fixtures for creating and managing BlogPost instances
in the test database. These fixtures streamline test setup by allowing individual
or bulk creation of blog posts, supporting various test cases such as pagination,
retrieval, and validation scenarios.

Fixtures:
- create_blog_post: Creates a single BlogPost instance with customizable attributes.
- seed_blog_posts: Seeds multiple BlogPost instances with a configurable count.
"""

from datetime import datetime, UTC
from typing import Callable, List, Optional

import pytest
from sqlalchemy.orm import Session

from app.domain.blog_post import BlogPost
from app.models.tables.blog_post import blog_posts


@pytest.fixture(scope='function')
def create_blog_post(session: Session) -> Callable[..., BlogPost]:
    """Creates and persists a BlogPost instance with customizable attributes.

    This fixture inserts a BlogPost record into the database with required fields,
    satisfying all NOT NULL and UNIQUE constraints. Returns a domain-level BlogPost
    object representing the inserted post (without the database ID).

    Args:
        session (Session): The SQLAlchemy session for database interactions.

    Returns:
        Callable[..., BlogPost]: A function that inserts and returns a BlogPost object.
    """

    def _create_blog_post(
        title: str = 'Test Blog Post',
        slug: str = 'test-blog-post',
        html_content: str = '<p>This is the content of the blog post.</p>',
        drive_file_id: str = 'unique_drive_file_id_1',
        meta_description: str = 'This is a test meta description.',
        keywords: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        read_time_minutes: int = 3,
        created_at: Optional[datetime] = None,
    ) -> BlogPost:
        if created_at is None:
            created_at = datetime.now(UTC)
        if keywords is None:
            keywords = ['test', 'blog']
        if categories is None:
            categories = ['testing', 'demo']

        query = blog_posts.insert().values(
            title=title,
            slug=slug,
            html_content=html_content,
            drive_file_id=drive_file_id,
            meta_description=meta_description,
            keywords=keywords,
            read_time_minutes=read_time_minutes,
            categories=categories,
            created_at=created_at
        ).returning(blog_posts.c.id)
        session.execute(query)
        session.commit()

        row = session.execute(
            blog_posts.select().where(blog_posts.c.title == title)
        ).fetchone()

        return BlogPost(
            title=title,
            slug=slug,
            html_content=html_content,
            drive_file_id=drive_file_id,
            meta_description=meta_description,
            keywords=keywords,
            read_time_minutes=read_time_minutes,
            categories=categories,
            created_at=created_at,
            updated_at=row.updated_at,
        )

    return _create_blog_post


@pytest.fixture(scope='function')
def seed_blog_posts(create_blog_post) -> Callable[[int], List[BlogPost]]:
    """Seeds a configurable number of blog posts using the create_blog_post fixture.

    This fixture generates a list of blog posts in the database to facilitate
    pagination and retrieval tests. The number of posts can be configured by the test.

    Args:
        create_blog_post (Callable[..., BlogPost]): Fixture for creating individual blog posts.

    Returns:
        Callable[[int], List[BlogPost]]: A function that accepts the desired number of blog posts to create.
    """

    def _seed_blog_posts(count: int = 25) -> List[BlogPost]:
        return [
            create_blog_post(
                title=f"Post {i + 1}",
                slug=f"post-{i + 1}",
                html_content=f"<p>Content {i + 1}</p>",
                drive_file_id=f"drive_id_{i + 1}",
                created_at=datetime.now(UTC)  # Always create timezone-aware timestamps
            ) for i in range(count)
        ]

    return _seed_blog_posts
