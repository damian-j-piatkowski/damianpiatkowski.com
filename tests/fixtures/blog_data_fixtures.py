"""Fixtures for seeding blog post data in tests.

This module provides reusable fixtures for creating and managing BlogPost instances
in the test database. These fixtures streamline test setup by allowing individual
or bulk creation of blog posts, supporting various test cases such as pagination,
retrieval, and validation scenarios.

Fixtures:
- create_blog_post: Creates a single BlogPost instance with customizable attributes.
- seed_blog_posts: Seeds multiple BlogPost instances with a configurable count.
"""

from typing import Callable, List, Optional

import pytest
from sqlalchemy.orm import Session

from app.domain.blog_post import BlogPost


@pytest.fixture(scope='function')
def create_blog_post(session: Session) -> Callable[..., BlogPost]:
    """Creates a BlogPost instance with customizable attributes.

    This fixture provides a BlogPost instance with default values for
    `title`, `content`, and `drive_file_id`. Users can override these
    defaults when creating the instance. The created BlogPost object
    is added to the session, but the commit responsibility is deferred
    to the calling test.

    Args:
        session (Session): The SQLAlchemy session for database interactions.

    Returns:
        Callable[..., BlogPost]: A function to create a BlogPost with specified attributes.
    """
    def _create_blog_post(
            title: Optional[str] = 'Test Blog Post',
            content: Optional[str] = 'This is the content of the blog post.',
            drive_file_id: Optional[str] = 'unique_drive_file_id_1'
    ) -> BlogPost:
        post = BlogPost(
            title=title,
            content=content,
            drive_file_id=drive_file_id
        )
        session.add(post)
        return post

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
        return [create_blog_post(f"Title {i}", f"Content {i}", f"drive_id_{i}") for i in range(count)]

    return _seed_blog_posts
