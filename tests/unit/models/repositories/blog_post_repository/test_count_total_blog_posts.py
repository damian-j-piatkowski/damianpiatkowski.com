"""Unit tests for the count_total_blog_posts repository method.

This module contains unit tests for the count_total_blog_posts method of
the BlogPostRepository class, verifying its behavior in counting the total number
of blog posts in the database.

Tests included:
    - test_count_total_blog_posts_empty: Ensures count is zero when no blog posts exist.
    - test_count_total_blog_posts_with_data: Verifies correct counting when blog posts exist.
    - test_count_total_blog_posts_large_dataset: Ensures correct count for a large dataset.
    - test_count_total_blog_posts_after_deletion: Ensures deleted posts do not affect the count.
    - test_count_total_blog_posts_after_concurrent_insert: Ensures counting reflects newly added posts.

Fixtures:
    - seed_blog_posts: Function fixture for seeding a specified number of blog posts.
    - create_blog_post: Creates an individual blog post.
    - session: Provides a database session.
"""

import pytest
from sqlalchemy import delete

from app.models.repositories.blog_post_repository import BlogPostRepository
from app.models.tables.blog_post import blog_posts  # Needed for deletion test


@pytest.mark.render_blog_posts
def test_count_total_blog_posts_empty(session):
    """Ensures count is zero when no blog posts exist."""
    repository = BlogPostRepository(session)
    total_posts = repository.count_total_blog_posts()
    assert total_posts == 0


@pytest.mark.render_blog_posts
def test_count_total_blog_posts_with_data(session, seed_blog_posts):
    """Verifies correct counting when blog posts exist."""
    seed_blog_posts(25)  # Ensure the database is populated before checking count
    session.commit()
    repository = BlogPostRepository(session)
    total_posts = repository.count_total_blog_posts()
    assert total_posts == 25


@pytest.mark.render_blog_posts
def test_count_total_blog_posts_large_dataset(session, seed_blog_posts):
    """Ensures correct count for a large dataset."""
    seed_blog_posts(500)  # Stress test
    session.commit()
    repository = BlogPostRepository(session)
    total_posts = repository.count_total_blog_posts()
    assert total_posts == 500


@pytest.mark.render_blog_posts
def test_count_total_blog_posts_after_deletion(session, seed_blog_posts):
    """Ensures deleted posts do not affect the count."""
    seed_blog_posts(25)
    session.commit()
    repository = BlogPostRepository(session)

    # Delete 5 posts manually
    session.execute(delete(blog_posts).where(blog_posts.c.id <= 5))
    session.commit()

    total_posts = repository.count_total_blog_posts()
    assert total_posts == 20  # 25 - 5 = 20


@pytest.mark.render_blog_posts
def test_count_total_blog_posts_after_concurrent_insert(session, seed_blog_posts, create_blog_post):
    """Ensures counting reflects newly added posts."""
    seed_blog_posts(10)
    session.commit()
    repository = BlogPostRepository(session)

    # Count before new insertion
    initial_count = repository.count_total_blog_posts()
    assert initial_count == 10

    # Insert 3 more posts
    create_blog_post("New Post 1", "test-blog-post-another", "Content 1", "drive_id_101")
    create_blog_post("New Post 2", "test-blog-post-and-another", "Content 2", "drive_id_102")
    create_blog_post("New Post 3", "test-blog-post-and-another-and-another", "Content 3", "drive_id_103")
    session.commit()

    # Count again
    new_count = repository.count_total_blog_posts()
    assert new_count == 13  # 10 + 3 = 13
