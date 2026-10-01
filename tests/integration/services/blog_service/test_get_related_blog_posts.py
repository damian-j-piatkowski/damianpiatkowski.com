"""Integration tests for blog_service.get_related_blog_posts.

Tests included:
    - test_get_related_blog_posts_shares_category: Verifies related posts exclude current slug.
"""

import pytest

from app.services.blog_service import get_related_blog_posts


@pytest.mark.render_blog_posts
def test_get_related_blog_posts_shares_category(session, create_blog_post) -> None:
    """Verifies that related posts share categories and exclude the current slug."""
    current = create_blog_post(
        title="Current",
        slug="current-post",
        categories=["Python", "Testing"],
        drive_file_id="drive_current",
    )
    related = create_blog_post(
        title="Related",
        slug="related-post",
        categories=["Python"],
        drive_file_id="drive_related",
    )
    create_blog_post(
        title="Unrelated",
        slug="unrelated-post",
        categories=["Travel"],
        drive_file_id="drive_unrelated",
    )
    session.commit()

    results = get_related_blog_posts(
        categories=current.categories,
        exclude_slug=current.slug,
        limit=5,
    )
    slugs = {post.slug for post in results}
    assert related.slug in slugs
    assert current.slug not in slugs
    assert "unrelated-post" not in slugs
