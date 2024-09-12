"""Tests for the BlogPost model.

This module contains tests for the CRUD operations on the BlogPost model,
ensuring that blog post-entries can be inserted, updated, deleted, and
queried correctly in the database.

Test functions:
- test_blog_post_create: Tests inserting a blog post into the database.
- test_blog_post_delete: Tests deleting a blog post from the database.
- test_blog_post_fetch_multiple: Tests querying multiple blog posts.
- test_blog_post_update: Tests updating a blog post in the database.
"""

from app.domain.blog_post import BlogPost


def test_blog_post_create(session, create_blog_post):
    """Test inserting a blog post into the database."""
    create_blog_post()  # Use fixture defaults
    session.commit()

    # Fetch the blog post from the database
    fetched_post = session.query(BlogPost).filter_by(title='Test Post').first()
    assert fetched_post is not None
    assert fetched_post.title == 'Test Post'
    assert fetched_post.content == 'This is a test post content'
    assert fetched_post.image_small == 'path/to/small/image.jpg'
    assert fetched_post.image_medium == 'path/to/medium/image.jpg'
    assert fetched_post.image_large == 'path/to/large/image.jpg'
    assert fetched_post.url == 'test-post'


def test_blog_post_delete(session, create_blog_post):
    """Test deleting a blog post from the database."""
    post = create_blog_post(title='Post to be deleted',
                            url='post-to-be-deleted')
    session.commit()

    # Delete the blog post
    session.delete(post)
    session.commit()

    # Verify the blog post has been deleted
    fetched_post = session.query(BlogPost).filter_by(
        title='Post to be deleted').first()
    assert fetched_post is None


def test_blog_post_fetch_multiple(session, create_blog_post):
    """Test querying multiple blog posts."""
    create_blog_post(title='Post 1', url='post-1')
    create_blog_post(title='Post 2', url='post-2')
    session.commit()

    # Fetch all blog posts
    fetched_posts = session.query(BlogPost).all()
    assert len(fetched_posts) == 2
    assert fetched_posts[0].title == 'Post 1'
    assert fetched_posts[1].title == 'Post 2'
    assert fetched_posts[0].url == 'post-1'
    assert fetched_posts[1].url == 'post-2'


def test_blog_post_update(session, create_blog_post):
    """Test updating a blog post in the database."""
    post = create_blog_post(
        title='Original Title',
        content='Original content',
        url='original-title'
    )
    session.commit()

    # Update the blog post
    post.title = 'Updated Title'
    post.content = 'Updated content'
    post.url = 'updated-title'
    session.commit()

    # Fetch the updated blog post
    updated_post = session.query(BlogPost).filter_by(
        title='Updated Title').first()
    assert updated_post is not None
    assert updated_post.title == 'Updated Title'
    assert updated_post.content == 'Updated content'
    assert updated_post.url == 'updated-title'
