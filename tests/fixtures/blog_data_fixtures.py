from typing import Callable, List, Optional

import pytest
from sqlalchemy.orm import Session

from app.domain.blog_post import BlogPost


@pytest.fixture(scope='function')
def create_blog_post(session: Session) -> Callable[..., BlogPost]:
    """
    Fixture to create a BlogPost instance with optional valid data.
    If no data is provided, it defaults to valid data.
    The commit responsibility is moved to the test.
    """

    def _create_blog_post(
            title: Optional[str] = 'Test Blog Post',
            content: Optional[str] = 'This is the content of the blog post.',
            image_small: Optional[str] = 'path/to/small.jpg',
            image_medium: Optional[str] = 'path/to/medium.jpg',
            image_large: Optional[str] = 'path/to/large.jpg',
            url: Optional[str] = 'http://example.com/test-post'
    ) -> BlogPost:
        post = BlogPost(
            title=title,
            content=content,
            image_small=image_small,
            image_medium=image_medium,
            image_large=image_large,
            url=url
        )
        session.add(post)
        return post

    return _create_blog_post


@pytest.fixture(scope='function')
def mock_db_posts() -> List[BlogPost]:
    """
    Fixture to create mock blog posts for testing, including edge cases.
    """
    return [
        BlogPost(
            title='Post 1', content='Content 1',
            image_small='', image_medium='', image_large='', url='post-1'
        ),
        BlogPost(
            title='Post 2', content='Content 2',
            image_small='', image_medium='', image_large='', url='post-2'
        ),
        BlogPost(
            title='Post 3', content='Content 3',
            image_small='', image_medium='', image_large='', url='post-3'
        ),
        BlogPost(
            title='Post with very long content', content='A' * 5000,
            image_small='', image_medium='', image_large='',
            url='post-long-content'
        ),
        BlogPost(
            title='Post with missing images', content='Content without images',
            image_small=None, image_medium=None, image_large=None,
            # type: ignore
            url='post-no-images'
        )
    ]
