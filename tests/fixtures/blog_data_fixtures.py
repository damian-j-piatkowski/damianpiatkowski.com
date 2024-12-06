"""Fixtures for testing BlogPost instances.

This module contains fixtures for creating and manipulating BlogPost instances
in tests. These fixtures include options for generating customizable blog posts
that can be added to the database session or used as mock data for unit tests.
They cover various use cases, including default blog post data, edge cases,
and missing fields.

Fixtures:
- create_blog_post: Creates a BlogPost instance with customizable fields.
- mock_db_posts: Provides a list of mock BlogPost instances for testing scenarios.
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
def mock_db_posts() -> List[BlogPost]:
    """Provides a list of mock BlogPost instances for testing.

    This fixture generates a list of BlogPost objects with various attributes,
    covering typical cases and edge cases (e.g., long content, missing `drive_file_id`).
    These instances do not interact with the database and are solely for mock use
    within tests.

    Returns:
        List[BlogPost]: A list of BlogPost instances with varying attributes.
    """
    return [
        BlogPost(
            title='Post 1', content='Content 1', drive_file_id='drive_file_1'
        ),
        BlogPost(
            title='Post 2', content='Content 2', drive_file_id='drive_file_2'
        ),
        BlogPost(
            title='Post 3', content='Content 3', drive_file_id='drive_file_3'
        ),
        BlogPost(
            title='Post with very long content', content='A' * 5000,
            drive_file_id='drive_file_long_content'
        ),
        BlogPost(
            title='Post with missing drive file ID', content='Content without drive file ID',
            drive_file_id=None  # type: ignore
        )
    ]
