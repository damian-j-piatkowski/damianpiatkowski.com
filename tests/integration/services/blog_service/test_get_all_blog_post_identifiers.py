"""Integration tests for the get_all_blog_post_identifiers service function.

This module verifies the behavior of the get_all_blog_post_identifiers service
in retrieving blog post identifiers (slug, title, drive_file_id) from the database.

Tests included:
    - test_returns_all_blog_post_identifiers: Verifies correct identifier retrieval.
    - test_raises_exception_on_database_error: Ensures proper exception is raised on DB failure.
    - test_returns_empty_list_when_no_posts_exist: Checks empty result when no posts exist.
    - test_handles_large_number_of_posts: Validates handling of many records.

Fixtures:
    - session: SQLAlchemy session for DB operations.
    - create_blog_post: Creates a single blog post.
    - seed_blog_posts: Seeds multiple blog posts for test scenarios.
"""

import pytest

from app.services.blog_service import get_all_blog_post_identifiers


@pytest.mark.admin_published_posts
@pytest.mark.admin_unpublished_posts
def test_returns_all_blog_post_identifiers(session, create_blog_post, caplog) -> None:
    """Should return identifiers for multiple blog posts and log appropriately."""
    create_blog_post(
        title="First Post",
        slug="first-post",
        drive_file_id="id_one"
    )
    create_blog_post(
        title="Second Post",
        slug="second-post",
        drive_file_id="id_two"
    )
    session.commit()

    with caplog.at_level("INFO"):
        result = get_all_blog_post_identifiers()

    assert len(result) == 2
    assert {"slug", "title", "drive_file_id"} <= result[0].keys()
    assert result[0]["title"] == "First Post"
    assert result[1]["drive_file_id"] == "id_two"

    assert "Fetching blog post identifiers from the repository." in caplog.text
    assert "Successfully fetched 2 blog post identifiers." in caplog.text


@pytest.mark.admin_published_posts
@pytest.mark.admin_unpublished_posts
def test_raises_exception_on_database_error(mocker, caplog) -> None:
    """Should raise RuntimeError when database access fails and log the error."""
    mocker.patch(
        "app.models.repositories.blog_post_repository.BlogPostRepository.fetch_all_post_identifiers",
        side_effect=RuntimeError("DB error")
    )

    with caplog.at_level("INFO"), pytest.raises(RuntimeError, match="Failed to retrieve blog post identifiers"):
        get_all_blog_post_identifiers()

    assert "Fetching blog post identifiers from the repository." in caplog.text
    assert "Error in BlogPostService: DB error" in caplog.text


@pytest.mark.admin_published_posts
@pytest.mark.admin_unpublished_posts
def test_returns_empty_list_when_no_posts_exist(session, caplog) -> None:
    """Should return an empty list when no blog posts are in the database."""
    with caplog.at_level("INFO"):
        result = get_all_blog_post_identifiers()

    assert result == []
    assert "Fetching blog post identifiers from the repository." in caplog.text
    assert "Successfully fetched 0 blog post identifiers." in caplog.text


@pytest.mark.admin_published_posts
@pytest.mark.admin_unpublished_posts
def test_handles_large_number_of_posts(session, seed_blog_posts, caplog) -> None:
    """Should return all identifiers correctly when many blog posts are present."""
    seed_blog_posts(30)

    with caplog.at_level("INFO"):
        result = get_all_blog_post_identifiers()

    assert len(result) == 30
    assert result[0]["slug"] == "post-1"
    assert result[-1]["title"] == "Post 30"

    assert "Fetching blog post identifiers from the repository." in caplog.text
    assert "Successfully fetched 30 blog post identifiers." in caplog.text
