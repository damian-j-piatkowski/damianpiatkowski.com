"""Integration tests for blog_service.get_blog_posts_by_category.

Tests included:
    - test_get_blog_posts_by_category_filters: Verifies category filtering and pagination.
"""

import pytest

from app.services.blog_service import get_blog_posts_by_category


@pytest.mark.render_blog_posts
def test_get_blog_posts_by_category_filters(session, create_blog_post) -> None:
    """Verifies that get_blog_posts_by_category returns only matching posts."""
    create_blog_post(title="Python Tips", slug="python-tips", categories=["Python"], drive_file_id="drive_py_1")
    create_blog_post(title="Flask Tips", slug="flask-tips", categories=["Flask"], drive_file_id="drive_fl_1")
    create_blog_post(title="More Python", slug="more-python", categories=["Python"], drive_file_id="drive_py_2")
    session.commit()

    posts, total_pages = get_blog_posts_by_category(page=1, per_page=10, category="Python")
    assert total_pages >= 1
    assert len(posts) == 2
    assert all("Python" in (post.categories or []) for post in posts)
