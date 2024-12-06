import pytest
import sqlalchemy.exc
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.domain.blog_post import BlogPost
from app.models.repositories.blog_post_repository import BlogPostRepository


# Test Case: Creating a blog post successfully
def test_create_blog_post_success(session):
    """Test case for successfully creating a blog post."""
    repository = BlogPostRepository(session)

    # Act: Create a blog post
    result = repository.create_blog_post(
        title='Unique Test Title',
        content='Test Content',
        drive_file_id='test-drive-file-id'
    )

    # Assert: Ensure the result matches and is in the session
    assert result.title == 'Unique Test Title'
    assert session.query(BlogPost).filter_by(
        title='Unique Test Title').one_or_none() is not None


# Test Case: Handling a failure when creating a blog post
def test_create_blog_post_failure(session, monkeypatch):
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
            drive_file_id='fail-drive-file-id'
        )


# Test Case: Fetching all blog posts successfully
def test_fetch_all_blog_posts_success(session, create_blog_post):
    # Arrange: Create multiple blog posts using the fixture
    create_blog_post(title='Post 1', content='Content 1', drive_file_id='file-id-1')
    create_blog_post(title='Post 2', content='Content 2', drive_file_id='file-id-2')
    session.commit()  # Commit changes to the database

    repository = BlogPostRepository(session)

    # Act: Fetch all blog posts
    posts = repository.fetch_all_blog_posts()

    # Assert: Ensure correct number of posts is returned and data matches
    assert len(posts) == 2
    assert posts[0].title == 'Post 1'
    assert posts[1].title == 'Post 2'


# Test Case: Handling long content (edge case)
def test_create_blog_post_with_excessively_long_content(session):
    """Test creating a blog post with content that's too long."""
    repository = BlogPostRepository(session)
    long_content = 'A' * 1000000000  # Very long content

    with pytest.raises(RuntimeError, match="Failed to create blog post"):
        repository.create_blog_post(
            title='Excessively Long Content Post',
            content=long_content,
            drive_file_id='long-content-file-id'
        )


# Test Case: Creating a blog post with missing content (edge case)
def test_create_blog_post_missing_content(session):
    """Test that creating a blog post without content raises IntegrityError."""
    repository = BlogPostRepository(session)

    # Act and Assert: Attempt to create the blog post without content
    with pytest.raises(IntegrityError, match="NOT NULL constraint failed: blog_posts.content"):
        repository.create_blog_post(
            title='Missing Content Post',
            content=None,  # type: ignore
            drive_file_id='missing-content-file-id'
        )


# Test Case: Creating a blog post with a duplicate title (edge case)
def test_create_blog_post_duplicate_title_failure(session, create_blog_post):
    """Test creating a blog post with a duplicate title."""
    repository = BlogPostRepository(session)

    # Arrange: Create the first post with a specific title
    create_blog_post(title="Duplicate Title", drive_file_id="unique-file-id")
    session.commit()

    # Act & Assert: Expect IntegrityError on duplicate title
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        repository.create_blog_post(
            title="Duplicate Title",
            content="Duplicate title content",
            drive_file_id="new-unique-file-id"
        )
