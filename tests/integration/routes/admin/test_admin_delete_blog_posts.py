"""Integration tests for the /admin/delete-blog-posts route.

This module verifies the behavior of the admin_delete_blog_posts route under
various conditions, including successful deletions, partial deletions,
missing posts, and critical errors.

Tests included:
    - test_admin_delete_blog_posts_all_success
    - test_admin_delete_blog_posts_partial_deletion
    - test_admin_delete_blog_posts_mixed_success_and_failure
    - test_admin_delete_blog_posts_missing_slug
    - test_admin_delete_blog_posts_no_slugs_provided
    - test_admin_delete_blog_posts_runtime_error

Fixtures:
    - client: Provides a Flask test client.
    - create_blog_post: Creates an individual blog post.
    - session: Provides a database session.
"""

import pytest

from app.exceptions import BlogPostNotFoundError
from app.models.repositories.blog_post_repository import BlogPostRepository


@pytest.mark.admin_delete_blog_posts
@pytest.mark.parametrize("count", [1, 2, 3, 4, 5])
def test_admin_delete_blog_posts_all_success(client, session, create_blog_post, count):
    """Successfully deletes 1 to 5 blog posts via the route."""
    slugs = []
    for i in range(count):
        slug = f"post-{i}"
        create_blog_post(f"Title {i}", slug, "Content", f"drive_id_{i}")
        slugs.append(slug)
    session.commit()

    response = client.delete("/admin/delete-blog-posts", json={"slugs": slugs})

    assert response.status_code == 200
    json_data = response.get_json()
    assert sorted(json_data["deleted"]) == sorted(slugs)
    assert json_data["errors"] == []

    # Verify posts are deleted from the database
    repository = BlogPostRepository(session)
    for slug in slugs:
        with pytest.raises(BlogPostNotFoundError):
            repository.fetch_blog_post_by_slug(slug)


@pytest.mark.admin_delete_blog_posts
@pytest.mark.parametrize("delete_count", [1, 2, 3, 4])
def test_admin_delete_blog_posts_partial_deletion(client, session, create_blog_post, delete_count):
    """Deletes a subset of posts and verifies remaining posts via the route."""
    total_slugs = []
    for i in range(5):
        slug = f"keep-post-{i}"
        create_blog_post(f"Keep Title {i}", slug, "Keep Content", f"keep_drive_id_{i}")
        total_slugs.append(slug)
    session.commit()

    slugs_to_delete = total_slugs[:delete_count]

    response = client.delete("/admin/delete-blog-posts", json={"slugs": slugs_to_delete})

    assert response.status_code == 200
    json_data = response.get_json()
    assert sorted(json_data["deleted"]) == sorted(slugs_to_delete)

    repository = BlogPostRepository(session)
    for slug in slugs_to_delete:
        with pytest.raises(BlogPostNotFoundError):
            repository.fetch_blog_post_by_slug(slug)

    remaining_slugs = total_slugs[delete_count:]
    for slug in remaining_slugs:
        assert repository.fetch_blog_post_by_slug(slug) is not None


@pytest.mark.admin_delete_blog_posts
def test_admin_delete_blog_posts_mixed_success_and_failure(client, session, create_blog_post):
    """Partial success with one valid and one non-existent slug via the route."""
    create_blog_post("Existing Post", "existing-post", "Content", "drive_id_exist")
    session.commit()

    slugs = ["existing-post", "missing-post"]

    response = client.delete("/admin/delete-blog-posts", json={"slugs": slugs})

    assert response.status_code == 207
    json_data = response.get_json()

    expected_json = {
        'deleted': ['existing-post'],
        'errors': [{'error': 'No blog post found with slug missing-post', 'slug': 'missing-post'}]
    }
    assert json_data == expected_json

    repository = BlogPostRepository(session)
    with pytest.raises(BlogPostNotFoundError):
        repository.fetch_blog_post_by_slug("existing-post")


@pytest.mark.admin_delete_blog_posts
def test_admin_delete_blog_posts_missing_slug(client, session):
    """Deletion fails for a non-existent slug via the route."""
    response = client.delete("/admin/delete-blog-posts", json={"slugs": ["nonexistent-post"]})

    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["deleted"] == []
    assert json_data["errors"][0]["slug"] == "nonexistent-post"


@pytest.mark.admin_delete_blog_posts
def test_admin_delete_blog_posts_no_slugs_provided(client):
    """Returns 400 when no slugs are provided in the request body."""
    response = client.delete("/admin/delete-blog-posts", json={"slugs": []})

    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["error"] == "No slugs provided for deletion"


@pytest.mark.admin_delete_blog_posts
def test_admin_delete_blog_posts_runtime_error(monkeypatch, client, session, create_blog_post):
    """Simulates a critical runtime error during deletion via the route."""
    create_blog_post("Error Post", "error-post", "Content", "drive_id_error")
    session.commit()

    def faulty_remove_blog_post_by_slug(slug):
        _ = slug
        raise RuntimeError("Simulated critical failure")

    monkeypatch.setattr("app.controllers.admin_controller.remove_blog_post_by_slug", faulty_remove_blog_post_by_slug)

    response = client.delete("/admin/delete-blog-posts", json={"slugs": ["error-post"]})

    assert response.status_code == 500
    json_data = response.get_json()

    expected_json = {
        'deleted': [],
        'errors': [{'error': 'Unexpected error: RuntimeError: Simulated critical failure', 'slug': 'error-post'}]
    }
    assert json_data == expected_json
