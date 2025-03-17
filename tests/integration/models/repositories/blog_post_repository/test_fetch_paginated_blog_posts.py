"""Integration tests for the fetch_paginated_blog_posts repository method.

This module contains integration tests for the fetch_paginated_blog_posts method of
the BlogPostRepository class, verifying its behavior in retrieving paginated blog
posts from the database under various conditions.

Tests included:
    - test_fetch_paginated_blog_posts_basic: Ensures correct pagination for a valid page request.
    - test_fetch_paginated_blog_posts_different_per_page_values: Verifies pagination behavior with varying per_page values.
    - test_fetch_paginated_blog_posts_last_page: Ensures the last page contains the remaining posts.
    - test_fetch_paginated_blog_posts_negative_page: Ensures requesting a negative page number defaults to page 1.
    - test_fetch_paginated_blog_posts_out_of_range: Ensures requesting a page beyond available pages returns an empty list.
    - test_fetch_paginated_blog_posts_page_zero: Ensures requesting page 0 defaults to page 1.

Fixtures:
    - seed_blog_posts: Function fixture for seeding a specified number of blog posts.
    - session: Provides a database session.
"""

from app.models.repositories.blog_post_repository import BlogPostRepository


def test_fetch_paginated_blog_posts_basic(session, seed_blog_posts):
    """Ensures correct pagination behavior for a valid page request."""
    seed_blog_posts(25)
    session.commit()
    repository = BlogPostRepository(session)
    posts, total_pages = repository.fetch_paginated_blog_posts(page=1, per_page=10)

    assert len(posts) == 10
    assert total_pages == 3  # 25 posts, 10 per page → 3 total pages
    assert posts[0].title == "Post 1"


def test_fetch_paginated_blog_posts_different_per_page_values(session, seed_blog_posts):
    """Verifies pagination behavior with varying per_page values, ensuring correct order."""
    seed_blog_posts(25)
    session.commit()
    repository = BlogPostRepository(session)

    posts_per_5, total_pages_per_5 = repository.fetch_paginated_blog_posts(page=1, per_page=5)
    posts_per_7, total_pages_per_7 = repository.fetch_paginated_blog_posts(page=1, per_page=7)
    posts_per_12, total_pages_per_12 = repository.fetch_paginated_blog_posts(page=1, per_page=12)
    posts_per_12_second_page, _ = repository.fetch_paginated_blog_posts(page=2, per_page=12)

    assert len(posts_per_5) == 5
    assert total_pages_per_5 == 5  # 25 posts, 5 per page → 5 pages

    assert len(posts_per_7) == 7
    assert total_pages_per_7 == 4  # 25 posts, 7 per page → 4 pages

    assert len(posts_per_12) == 12
    assert total_pages_per_12 == 3  # 25 posts, 12 per page → 3 pages (last page will have 1 post)

    # Order verification
    expected_titles_page_1 = [f"Post {i}" for i in range(1, 13)]  # Posts 1-12
    expected_titles_page_2 = [f"Post {i}" for i in range(13, 25)]  # Posts 13-24

    assert [post.title for post in posts_per_12] == expected_titles_page_1
    assert [post.title for post in posts_per_12_second_page] == expected_titles_page_2



def test_fetch_paginated_blog_posts_last_page(session, seed_blog_posts):
    """Ensures the last page contains the remaining posts."""
    seed_blog_posts(25)
    session.commit()
    repository = BlogPostRepository(session)
    posts, total_pages = repository.fetch_paginated_blog_posts(page=3, per_page=10)

    assert len(posts) == 5  # Last page should have 5 posts
    assert total_pages == 3


def test_fetch_paginated_blog_posts_negative_page(session, seed_blog_posts):
    """Ensures requesting a negative page number defaults to page 1."""
    seed_blog_posts(25)
    session.commit()
    repository = BlogPostRepository(session)
    posts_neg, total_pages_neg = repository.fetch_paginated_blog_posts(page=-3, per_page=10)
    posts_page_1, total_pages_1 = repository.fetch_paginated_blog_posts(page=1, per_page=10)

    assert len(posts_neg) == len(posts_page_1)
    assert total_pages_neg == total_pages_1


def test_fetch_paginated_blog_posts_out_of_range(session, seed_blog_posts):
    """Ensures requesting a page beyond the total available pages returns an empty list."""
    seed_blog_posts(25)
    session.commit()
    repository = BlogPostRepository(session)
    posts, total_pages = repository.fetch_paginated_blog_posts(page=5, per_page=10)

    assert len(posts) == 0
    assert total_pages == 3


def test_fetch_paginated_blog_posts_page_zero(session, seed_blog_posts):
    """Ensures requesting page 0 defaults to page 1."""
    seed_blog_posts(25)
    session.commit()
    repository = BlogPostRepository(session)
    posts_page_0, total_pages_0 = repository.fetch_paginated_blog_posts(page=0, per_page=10)
    posts_page_1, total_pages_1 = repository.fetch_paginated_blog_posts(page=1, per_page=10)

    assert len(posts_page_0) == len(posts_page_1)
    assert total_pages_0 == total_pages_1
