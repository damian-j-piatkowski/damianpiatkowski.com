"""Integration tests for the /admin/unpublished-posts route.

This module verifies the integration between the Flask route `/admin/unpublished-posts`
and the `find_unpublished_drive_articles` controller. It tests how the route responds
to different backend conditions, including API errors, permission issues, and various
data states in the database and Google Drive.

Test Functions:
    - test_unpublished_posts_all_articles_published
    - test_unpublished_posts_empty_database_and_folder
    - test_unpublished_posts_google_drive_api_error
    - test_unpublished_posts_no_folder_id
    - test_unpublished_posts_permission_error
    - test_unpublished_posts_some_articles_unpublished

Fixtures:
    - app: Provides the Flask app context.
    - client: A test client for making HTTP requests.
    - session: SQLAlchemy session for database verification.
    - create_blog_post: Creates a blog post entry in the DB.
    - test_drive_file_metadata_map: Provides file metadata for integration.
    - mocker: Used to patch Drive service behavior in error scenarios.
"""

import pytest
from flask import current_app

from app import exceptions


@pytest.mark.admin_unpublished_posts
@pytest.mark.api
def test_unpublished_posts_all_articles_published(client, session, create_blog_post, test_drive_file_metadata_map):
    """Verifies that the route returns an empty list when all Drive files are already published in the database."""
    for metadata in test_drive_file_metadata_map.values():
        create_blog_post(
            title=metadata["title"],
            slug=metadata["slug"],
            html_content="<p>Some content</p>",
            drive_file_id=metadata["file_id"],
        )
    session.commit()

    response = client.get("/admin/unpublished-posts")
    assert response.status_code == 200
    assert response.get_json() == []


@pytest.mark.admin_unpublished_posts
@pytest.mark.parametrize("mock_google_drive_service",
                         [{"patch_target": "app.services.google_drive_service.GoogleDriveService",
                           "list_folder_contents_return": []}], indirect=True)
def test_unpublished_posts_empty_database_and_folder(client, mock_google_drive_service, session):
    """Verifies that the route returns an empty list when both the DB and Google Drive folder are empty."""
    response = client.get("/admin/unpublished-posts")
    assert response.status_code == 200
    assert response.get_json() == []


@pytest.mark.admin_unpublished_posts
@pytest.mark.parametrize("mock_google_drive_service",
                         [{
                             "patch_target": "app.controllers.admin_controller.GoogleDriveService",
                             "list_folder_contents_side_effect": exceptions.GoogleDriveAPIError("Google Drive API error")
                         }],
                         indirect=True)
def test_unpublished_posts_google_drive_api_error(client, mock_google_drive_service, session):
    """Verifies that the route returns a 500 error with a message when a Google Drive API error occurs."""

    response = client.get("/admin/unpublished-posts")

    # Sanity check: ensure the side effect got used
    mock_google_drive_service.list_folder_contents.assert_called_once()

    assert response.status_code == 500



@pytest.mark.admin_unpublished_posts
def test_unpublished_posts_no_folder_id(app, client, monkeypatch, session):
    """Verifies that the route returns a 500 error when the DRIVE_BLOG_POSTS_FOLDER_ID config is missing."""
    with app.app_context():
        monkeypatch.setitem(current_app.config, "DRIVE_BLOG_POSTS_FOLDER_ID", None)

        response = client.get("/admin/unpublished-posts")
        assert response.status_code == 500
        assert response.get_json() == {
            "error": "Google Drive folder ID is missing in the configuration"
        }



@pytest.mark.admin_unpublished_posts
@pytest.mark.parametrize("mock_google_drive_service",
                         [{
                             "patch_target": "app.controllers.admin_controller.GoogleDriveService"
                         }],
                         indirect=True)
def test_unpublished_posts_permission_error(client, mock_google_drive_service, session):
    """Verifies that the route returns a 403 error when a Google Drive permission error occurs."""
    mock_google_drive_service.list_folder_contents.side_effect = exceptions.GoogleDrivePermissionError(
        "Insufficient permissions for Google Drive access"
    )

    response = client.get("/admin/unpublished-posts")
    assert response.status_code == 403
    assert response.get_json() == {
        "error": "Insufficient permissions for Google Drive access"
    }


@pytest.mark.admin_unpublished_posts
@pytest.mark.api
def test_unpublished_posts_some_articles_unpublished(client, session, create_blog_post, test_drive_file_metadata_map):
    """Verifies that the route returns only Drive articles that are not yet published in the database."""
    design_metadata = test_drive_file_metadata_map["design_principles"]
    value_metadata = test_drive_file_metadata_map["value_objects"]

    create_blog_post(
        title=design_metadata["title"],
        slug=design_metadata["slug"],
        html_content="<p>Already published content.</p>",
        drive_file_id=design_metadata["file_id"]
    )
    session.commit()

    response = client.get("/admin/unpublished-posts")
    assert response.status_code == 200

    slugs = [item["slug"] for item in response.get_json()]
    assert value_metadata["slug"] in slugs
    assert design_metadata["slug"] not in slugs
