"""Integration tests for blog_service.get_all_categories_with_counts.

Tests included:
    - test_get_all_categories_with_counts_seeded: Verifies category counts and total posts.
"""

import pytest

from app.services.blog_service import get_all_categories_with_counts


@pytest.mark.render_blog_posts
def test_get_all_categories_with_counts_seeded(session, create_blog_post) -> None:
    """Verifies that category counts reflect seeded posts and total post count."""
    create_blog_post(title="A", slug="a", categories=["Python"], drive_file_id="drive_a")
    create_blog_post(title="B", slug="b", categories=["Python", "Flask"], drive_file_id="drive_b")
    create_blog_post(title="C", slug="c", categories=["Travel"], drive_file_id="drive_c")
    session.commit()

    categories, total_posts = get_all_categories_with_counts()
    counts = {name: count for name, count in categories}
    assert total_posts == 3
    assert counts.get("Python") == 2
    assert counts.get("Flask") == 1
    assert counts.get("Travel") == 1
