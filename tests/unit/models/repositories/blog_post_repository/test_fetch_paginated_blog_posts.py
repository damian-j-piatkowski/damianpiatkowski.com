import pytest
from app.models.repositories.blog_post_repository import BlogPostRepository
from app.domain.blog_post import BlogPost

@pytest.fixture
def seeded_blog_posts(session):
    """Seed test data into the database."""
    repository = BlogPostRepository(session)
    posts = [
        repository.create_blog_post(f"Title {i}", f"Content {i}", f"drive_id_{i}")
        for i in range(25)
    ]
    return posts

def test_fetch_paginated_blog_posts_basic(session, seeded_blog_posts):
    """Ensure correct pagination behavior for a valid page request."""
    repository = BlogPostRepository(session)
    page, per_page = 1, 10
    posts, total_pages = repository.fetch_paginated_blog_posts(page, per_page)

    assert len(posts) == 10
    assert total_pages == 3  # 25 posts, 10 per page → 3 total pages
    assert posts[0].title == "Title 0"

def test_fetch_paginated_blog_posts_last_page(session, seeded_blog_posts):
    """Ensure the last page contains the remaining posts."""
    repository = BlogPostRepository(session)
    page, per_page = 10, 10
    posts, total_pages = repository.fetch_paginated_blog_posts(3, per_page)

    assert len(posts) == 5  # Last page should have 5 posts
    assert total_pages == 3

def test_fetch_paginated_blog_posts_out_of_range(session, seeded_blog_posts):
    """Ensure requesting a page beyond the total available pages returns an empty list."""
    repository = BlogPostRepository(session)
    page, per_page = 5, 10
    posts, total_pages = repository.fetch_paginated_blog_posts(page, per_page)

    assert len(posts) == 0
    assert total_pages == 3

def test_fetch_paginated_blog_posts_page_zero(session, seeded_blog_posts):
    """Ensure requesting page 0 defaults to page 1."""
    repository = BlogPostRepository(session)
    posts_page_0, total_pages_0 = repository.fetch_paginated_blog_posts(0, 10)
    posts_page_1, total_pages_1 = repository.fetch_paginated_blog_posts(1, 10)

    assert posts_page_0 == posts_page_1
    assert total_pages_0 == total_pages_1

def test_fetch_paginated_blog_posts_negative_page(session, seeded_blog_posts):
    """Ensure requesting a negative page number defaults to page 1."""
    repository = BlogPostRepository(session)
    posts_neg, total_pages_neg = repository.fetch_paginated_blog_posts(-3, 10)
    posts_page_1, total_pages_1 = repository.fetch_paginated_blog_posts(1, 10)

    assert posts_neg == posts_page_1
    assert total_pages_neg == total_pages_1
