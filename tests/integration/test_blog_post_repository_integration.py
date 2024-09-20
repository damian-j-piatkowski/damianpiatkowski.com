import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.domain.blog_post import BlogPost
from app.models.repositories.blog_post_repository import BlogPostRepository


# Test Case: Creating a blog post successfully
def test_create_blog_post_success(session, _db):
    repository = BlogPostRepository(session)

    # Act: Create a blog post with the required 'url' field
    result = repository.create_blog_post(
        title='Test Title',
        content='Test Content',
        image_small='small.jpg',
        image_medium='medium.jpg',
        image_large='large.jpg',
        url='test-url'  # Add the URL parameter
    )
    session.commit()

    saved_post = session.query(BlogPost).filter_by(
        title='Test Title').one_or_none()
    assert saved_post is not None
    assert saved_post.content == 'Test Content'
    assert result['title'] == 'Test Title'


# Test Case: Fetching all blog posts successfully
def test_fetch_all_blog_posts_success(session, create_blog_post, _db):
    # Arrange: Create a couple of blog posts with unique URLs
    create_blog_post(title='Post 1', content='Content 1', url='url-1')
    create_blog_post(title='Post 2', content='Content 2', url='url-2')
    session.commit()  # Commit changes to the in-memory DB

    repository = BlogPostRepository(session)

    # Act: Fetch all blog posts from the repository
    posts = repository.fetch_all_blog_posts()

    # Assert: Ensure two posts are returned and the data matches
    assert len(posts) == 2
    assert posts[0]['title'] == 'Post 1'
    assert posts[1]['title'] == 'Post 2'


# Test Case: Fetching all blog posts when none exist (empty DB)
def test_fetch_all_blog_posts_empty(session, _db):
    # Arrange: Ensure no blog posts exist
    repository = BlogPostRepository(session)

    # Act: Fetch all blog posts
    posts = repository.fetch_all_blog_posts()

    # Assert: The returned list should be empty
    assert len(posts) == 0


# Test Case: Creating a blog post with very long content (edge case)
def test_create_blog_post_with_long_content(session, _db):
    long_content = 'A' * 10000  # 10,000 characters of content
    repository = BlogPostRepository(session)

    result = repository.create_blog_post(
        title='Long Content Post',
        content=long_content,
        image_small='small.jpg',
        image_medium='medium.jpg',
        image_large='large.jpg',
        url='long-content-url'  # Add the URL parameter
    )
    session.commit()

    saved_post = session.query(BlogPost).filter_by(
        title='Long Content Post').one_or_none()
    assert saved_post is not None
    assert saved_post.content == long_content
    assert result['title'] == 'Long Content Post'


# Test Case: Creating a blog post with missing images (edge case)
def test_create_blog_post_missing_images(session, _db):
    # Arrange: Create a blog post with missing image fields (None)
    repository = BlogPostRepository(session)

    # Act: Create the blog post with missing images
    result = repository.create_blog_post(
        title='Post with No Images',
        content='Content without images',
        image_small=None,  # type: ignore
        image_medium=None,  # type: ignore
        image_large=None,  # type: ignore
        url='test-url',
    )
    session.commit()  # Commit changes to the DB

    # Assert: Ensure the post is created and stored correctly
    saved_post = session.query(BlogPost).filter_by(
        title='Post with No Images').one_or_none()
    assert saved_post is not None
    assert saved_post.image_small is None
    assert saved_post.image_medium is None
    assert saved_post.image_large is None
    assert result['title'] == 'Post with No Images'


# Test Case: Handling a failure when creating a blog post (DB error)
def test_create_blog_post_failure(session, monkeypatch, _db):
    # Arrange: Monkeypatch the session's `execute` method to raise an error
    repository = BlogPostRepository(session)
    monkeypatch.setattr(session, 'execute',
                        lambda *args, **kwargs: (_ for _ in ()).throw(
                            SQLAlchemyError()))

    # Act & Assert: Ensure that a RuntimeError is raised when the DB
    # operation fails
    with pytest.raises(RuntimeError,
                       match="Failed to create blog post in the database."):
        repository.create_blog_post(
            title='Fail Title',
            content='Fail Content',
            image_small='small.jpg',
            image_medium='medium.jpg',
            image_large='large.jpg',
            url='test-url'
        )


# Test Case: Fetching all blog posts including edge cases using mock_db_posts
def test_fetch_all_blog_posts_with_mock_data(session, mock_db_posts, _db):
    # Arrange: Add mock blog posts to the session
    for post in mock_db_posts:
        session.add(post)
    session.commit()

    repository = BlogPostRepository(session)

    # Act: Fetch all blog posts
    posts = repository.fetch_all_blog_posts()

    # Assert: Ensure the correct number of posts and edge case handling
    assert len(posts) == len(mock_db_posts)
    assert posts[3]['title'] == 'Post with very long content'
    assert len(posts[3]['content']) == 5000
    assert posts[4]['title'] == 'Post with missing images'
    assert posts[4]['image_small'] is None
    assert posts[4]['image_medium'] is None
    assert posts[4]['image_large'] is None
