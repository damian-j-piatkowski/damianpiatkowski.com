from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.domain.blog_post import BlogPost
from app.models.repositories.blog_post_repository import BlogPostRepository


# Test Case: Creating a blog post successfully
def test_create_blog_post_success(session):
    """Test case for successfully creating a blog post."""
    # Arrange: Use the session and repository from the fixture
    repository = BlogPostRepository(session)

    # Act: Create a blog post
    result = repository.create_blog_post(
        title='Unique Test Title',  # Use a unique title and URL
        content='Test Content',
        image_small='small.jpg',
        image_medium='medium.jpg',
        image_large='large.jpg',
        url='unique-url'  # Added URL parameter
    )

    # Assert: Ensure the result matches and is in the session
    assert result['title'] == 'Unique Test Title'
    assert session.query(BlogPost).filter_by(
        title='Unique Test Title').one_or_none() is not None


# Test Case: Handling duplicate URL failure
def test_create_blog_post_duplicate_url_failure(session, create_blog_post):
    """Test case for creating a blog post with a duplicate URL."""
    repository = BlogPostRepository(session)

    # Arrange: Create the first post with a specific URL
    create_blog_post(title="Test Post 1", url="duplicate-url")
    session.commit()

    # Act & Assert: Expect RuntimeError on duplicate URL
    with pytest.raises(RuntimeError, match="Failed to create blog post in the database."):
        repository.create_blog_post(
            title='Test Post 2',
            content='Content with duplicate URL',
            image_small='small.jpg',
            image_medium='medium.jpg',
            image_large='large.jpg',
            url='duplicate-url'  # Same URL as the first post
        )



# Test Case: Handling a failure when creating a blog post
def test_create_blog_post_failure(session, monkeypatch):
    # Arrange: Mock session execution to raise a SQLAlchemyError
    repository = BlogPostRepository(session)
    monkeypatch.setattr(session, 'execute',
                        lambda *args, **kwargs: (_ for _ in ()).throw(
                            SQLAlchemyError()))

    # Act & Assert: RuntimeError should be raised due to SQLAlchemyError
    with pytest.raises(RuntimeError,
                       match="Failed to create blog post in the database."):
        repository.create_blog_post(
            title='Fail Title',
            content='Fail Content',
            image_small='small.jpg',
            image_medium='medium.jpg',
            image_large='large.jpg',
            url='fail-url'
        )


# Test Case: Fetching all blog posts successfully
def test_fetch_all_blog_posts_success(session, create_blog_post):
    # Arrange: Create multiple blog posts using the fixture
    create_blog_post(title='Post 1', content='Content 1', url='post-1-url')
    create_blog_post(title='Post 2', content='Content 2', url='post-2-url')
    session.commit()  # Commit changes to the database

    repository = BlogPostRepository(session)

    # Act: Fetch all blog posts
    posts = repository.fetch_all_blog_posts()

    # Assert: Ensure correct number of posts is returned and data matches
    assert len(posts) == 2
    assert posts[0]['title'] == 'Post 1'
    assert posts[1]['title'] == 'Post 2'


# Test Case: Fetching all blog posts using mock_db_posts (edge cases included)
def test_fetch_all_blog_posts_with_mock_data_failure(session, mock_db_posts):
    """Test for failure when fetching blog posts."""
    repository = BlogPostRepository(session)

    # Simulate a failure in the repository (e.g., SQLAlchemyError)
    session.execute = MagicMock(side_effect=SQLAlchemyError)

    with pytest.raises(RuntimeError, match="Failed to fetch blog posts"):
        repository.fetch_all_blog_posts()


# Test Case: Fetching all blog posts with no data (edge case)
def test_fetch_all_blog_posts_empty(session, monkeypatch):
    # Arrange: Ensure repository will fail when fetching
    repository = BlogPostRepository(session)

    # Simulate a failure in the repository (e.g., SQLAlchemyError)
    monkeypatch.setattr(session, 'execute', lambda *args, **kwargs: (_ for _ in ()).throw(SQLAlchemyError()))

    # Act & Assert: Expect a RuntimeError due to the SQLAlchemyError
    with pytest.raises(RuntimeError, match="Failed to fetch blog posts from the database"):
        repository.fetch_all_blog_posts()



# Test Case: Handling long content (edge case)
def test_create_blog_post_with_excessively_long_content(session):
    """Test creating a blog post with content that's too long."""
    repository = BlogPostRepository(session)
    long_content = 'A' * 1000000000  # Very long content

    with pytest.raises(RuntimeError, match="Failed to create blog post"):
        repository.create_blog_post(
            title='Excessively Long Content Post',
            content=long_content,
            image_small='small.jpg',
            image_medium='medium.jpg',
            image_large='large.jpg',
            url='long-content-url'
        )


# Test Case: Creating a blog post with missing images (edge case)
def test_create_blog_post_missing_images(session):
    # Arrange: Create a blog post with None for images
    repository = BlogPostRepository(session)

    # Act: Create the blog post with missing image URLs
    result = repository.create_blog_post(
        title='Post with No Images',
        content='Content without images',
        image_small=None,  # type: ignore
        image_medium=None,  # type: ignore
        image_large=None,  # type: ignore
        url='post-no-images-url'  # Added URL parameter
    )

    # Assert: Ensure the post is created and has None values for images
    assert result['title'] == 'Post with No Images'
    assert result['image_small'] is None
    assert result['image_medium'] is None
    assert result['image_large'] is None
