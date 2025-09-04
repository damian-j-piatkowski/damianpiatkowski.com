"""Integration tests for the delete_blog_posts controller function.

This module contains integration tests verifying the behavior of the
delete_blog_posts function under various conditions, including successful
deletions, partial deletions, missing posts, and critical errors.

Tests included:
    - test_delete_blog_posts_all_success: Successfully deletes 1-5 posts.
    - test_delete_blog_posts_mixed_success_and_failure: Partial success with one missing slug.
    - test_delete_blog_posts_missing_slug: Deletion fails for a non-existent slug.
    - test_delete_blog_posts_no_slugs_provided: Returns 400 when no slugs are provided.
    - test_delete_blog_posts_partial_deletion: Deletes a subset of posts and verifies remaining posts.
    - test_delete_blog_posts_runtime_error: Simulates a runtime error during deletion.

Fixtures:
    - create_blog_post: Creates an individual blog post.
    - session: Provides a database session.
"""

import pytest

from app.controllers.admin_controller import delete_blog_posts
from app.exceptions import BlogPostNotFoundError
from app.models.repositories.blog_post_repository import BlogPostRepository


@pytest.mark.admin_delete_blog_posts
@pytest.mark.parametrize("count", [1, 2, 3, 4, 5])
def test_delete_blog_posts_all_success(session, create_blog_post, count):
    """Successfully deletes 1 to 5 blog posts."""
    slugs = []
    for i in range(count):
        slug = f"post-{i}"
        create_blog_post(f"Title {i}", slug, "Content", f"drive_id_{i}")
        slugs.append(slug)
    session.commit()

    response, status_code = delete_blog_posts(slugs)

    assert status_code == 200
    assert sorted(response.json["deleted"]) == sorted(slugs)
    assert response.json["errors"] == []

    # Verify all posts are gone
    repository = BlogPostRepository(session)
    for slug in slugs:
        with pytest.raises(BlogPostNotFoundError):
            repository.fetch_blog_post_by_slug(slug)


@pytest.mark.admin_delete_blog_posts
@pytest.mark.parametrize("delete_count", [1, 2, 3, 4])
def test_delete_blog_posts_partial_deletion(session, create_blog_post, delete_count):
    """Deletes a subset of posts and verifies remaining posts exist."""
    total_slugs = []
    for i in range(5):
        slug = f"keep-post-{i}"
        create_blog_post(f"Keep Title {i}", slug, "Keep Content", f"keep_drive_id_{i}")
        total_slugs.append(slug)
    session.commit()

    slugs_to_delete = total_slugs[:delete_count]

    response, status_code = delete_blog_posts(slugs_to_delete)

    assert status_code == 200
    assert sorted(response.json["deleted"]) == sorted(slugs_to_delete)

    # Verify deleted ones are gone
    repository = BlogPostRepository(session)
    for slug in slugs_to_delete:
        with pytest.raises(BlogPostNotFoundError):
            repository.fetch_blog_post_by_slug(slug)

    # Verify others are still present
    remaining_slugs = total_slugs[delete_count:]
    for slug in remaining_slugs:
        assert repository.fetch_blog_post_by_slug(slug) is not None


@pytest.mark.admin_delete_blog_posts
def test_delete_blog_posts_mixed_success_and_failure(session, create_blog_post):
    """Partial success with a valid and a non-existent slug."""
    create_blog_post("Existing Post", "existing-post", "Content", "drive_id_exist")
    session.commit()

    slugs = ["existing-post", "missing-post"]

    response, status_code = delete_blog_posts(slugs)

    expected_json = {
        'deleted': ['existing-post'],
        'errors': [{'error': 'No blog post found with slug missing-post', 'slug': 'missing-post'}]
    }
    assert status_code == 207
    assert response.json == expected_json

    repository = BlogPostRepository(session)
    with pytest.raises(BlogPostNotFoundError):
        repository.fetch_blog_post_by_slug("existing-post")


@pytest.mark.admin_delete_blog_posts
def test_delete_blog_posts_missing_slug(session):
    """Deletion fails for a non-existent slug."""
    slugs = ["nonexistent-post"]

    response, status_code = delete_blog_posts(slugs)

    assert status_code == 400
    assert response.json["deleted"] == []
    assert response.json["errors"][0]["slug"] == "nonexistent-post"


@pytest.mark.admin_delete_blog_posts
def test_delete_blog_posts_no_slugs_provided(session):
    """Returns 400 when no slugs are provided."""
    response, status_code = delete_blog_posts([])

    assert status_code == 400
    assert response.json["error"] == "No slugs provided for deletion"


@pytest.mark.admin_delete_blog_posts
def test_delete_blog_posts_runtime_error(monkeypatch, session, create_blog_post):
    """Simulates a critical runtime error during deletion."""
    create_blog_post("Error Post", "error-post", "Content", "drive_id_error")
    session.commit()

    def faulty_remove_blog_post_by_slug(slug):
        _ = slug
        raise RuntimeError("Simulated critical failure")

    # Patch the service function to raise RuntimeError
    monkeypatch.setattr("app.controllers.admin_controller.remove_blog_post_by_slug", faulty_remove_blog_post_by_slug)

    slugs = ["error-post"]

    response, status_code = delete_blog_posts(slugs)
    expected_json = {
        'deleted': [],
        'errors': [{'error': 'Unexpected error: RuntimeError: Simulated critical failure', 'slug': 'error-post'}]}

    assert status_code == 500
    assert response.json == expected_json
