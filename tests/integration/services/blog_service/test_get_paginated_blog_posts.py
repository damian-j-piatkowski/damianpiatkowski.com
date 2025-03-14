"""Integration tests for the get_paginated_blog_posts service function.

This module contains integration tests for the get_paginated_blog_posts service,
verifying its behavior in retrieving paginated blog posts from the database under various conditions.

Tests included:
    - test_get_paginated_blog_posts_empty: Ensures that requesting pagination when no posts exist returns an empty list.
    - test_get_paginated_blog_posts_invalid_page: Checks that requesting page=0 or negative page numbers defaults to page 1.
    - test_get_paginated_blog_posts_multiple_pages: Verifies pagination across multiple pages, ensuring correct ordering.
    - test_get_paginated_blog_posts_out_of_range: Ensures requesting a page beyond the total available pages returns an empty list.
    - test_get_paginated_blog_posts_single_page: Verifies pagination when all posts fit within a single page.

Fixtures:
    - create_blog_post: Fixture to create blog posts in the database.
    - session: Provides a session object for database interactions.
"""

from app.services.blog_service import get_paginated_blog_posts


def test_get_paginated_blog_posts_empty(session) -> None:
    """Ensures requesting pagination when no posts exist returns an empty list."""
    posts, total_pages = get_paginated_blog_posts(page=1, per_page=10)
    assert posts == []
    assert total_pages == 0


def test_get_paginated_blog_posts_invalid_page(session, create_blog_post) -> None:
    """Checks that requesting page=0 or negative page numbers defaults to page 1."""
    create_blog_post(title="Valid Post 1", content="Content 1", drive_file_id="id_1")
    create_blog_post(title="Valid Post 2", content="Content 2", drive_file_id="id_2")
    session.commit()

    posts_zero, total_pages_zero = get_paginated_blog_posts(page=0, per_page=10)
    posts_negative, total_pages_negative = get_paginated_blog_posts(page=-5, per_page=10)

    assert posts_zero == posts_negative
    assert total_pages_zero == total_pages_negative
    assert len(posts_zero) == 2
    assert total_pages_zero == 1


def test_get_paginated_blog_posts_single_page(session, create_blog_post) -> None:
    """Verifies pagination when all posts fit within a single page."""
    for i in range(7):
        create_blog_post(title=f"Post {i + 1}", content=f"Content {i + 1}", drive_file_id=f"id_{i + 1}")
    session.commit()

    posts, total_pages = get_paginated_blog_posts(page=1, per_page=10)

    assert len(posts) == 7
    assert total_pages == 1
    assert posts[0].title == "Post 1"
    assert posts[-1].title == "Post 7"


def test_get_paginated_blog_posts_multiple_pages(session, create_blog_post) -> None:
    """Verifies pagination across multiple pages, ensuring correct ordering."""
    for i in range(32):
        create_blog_post(title=f"Post {i + 1}", content=f"Content {i + 1}", drive_file_id=f"id_{i + 1}")
    session.commit()

    page_1_posts, total_pages = get_paginated_blog_posts(page=1, per_page=10)
    page_2_posts, _ = get_paginated_blog_posts(page=2, per_page=10)
    page_3_posts, _ = get_paginated_blog_posts(page=3, per_page=10)
    page_4_posts, _ = get_paginated_blog_posts(page=4, per_page=10)

    assert total_pages == 4
    assert len(page_1_posts) == 10
    assert len(page_2_posts) == 10
    assert len(page_3_posts) == 10
    assert len(page_4_posts) == 2

    assert page_1_posts[0].title == "Post 1"
    assert page_1_posts[-1].title == "Post 10"
    assert page_2_posts[0].title == "Post 11"
    assert page_2_posts[-1].title == "Post 20"
    assert page_3_posts[0].title == "Post 21"
    assert page_3_posts[-1].title == "Post 30"
    assert page_4_posts[0].title == "Post 31"
    assert page_4_posts[-1].title == "Post 32"


def test_get_paginated_blog_posts_out_of_range(session, create_blog_post) -> None:
    """Ensures requesting a page beyond the total available pages returns an empty list."""
    for i in range(15):
        create_blog_post(title=f"Post {i + 1}", content=f"Content {i + 1}", drive_file_id=f"id_{i + 1}")
    session.commit()

    posts, total_pages = get_paginated_blog_posts(page=5, per_page=10)

    assert total_pages == 2  # Only 2 pages exist
    assert posts == []
