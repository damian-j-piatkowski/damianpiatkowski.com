"""Integration tests for the find_unpublished_drive_articles controller function.

This module contains integration tests for the find_unpublished_drive_articles
controller function, focusing on interactions with Google Drive and the in-memory
database. The tests verify that the service correctly identifies unpublished
articles under various conditions.

Tests included:
    - test_find_unpublished_drive_articles_all_articles_published: Verifies the function
      behavior when all articles are already published.
    - test_find_unpublished_drive_articles_empty_database_and_folder: Tests with no
      blog posts in the database and no files in Google Drive.
    - test_find_unpublished_drive_articles_google_drive_api_error: Tests handling of a
      general Google Drive API error.
    - test_find_unpublished_drive_articles_no_folder_id: Ensures the function handles
      the case where the Google Drive folder ID is missing in the config.
    - test_find_unpublished_drive_articles_permission_error: Tests handling of a
      Google Drive permission error.
    - test_find_unpublished_drive_articles_success: Verifies the function detects
      unpublished articles when some are missing from the database.

Fixtures:
    - app: Provides the Flask application context for the tests.
    - create_blog_post: Fixture to create blog posts in the database.
    - mocker: Provides mocking utilities for mocking external services.
    - session: Provides a session object for database interactions.
    - test_drive_file_metadata_map: Provides a mapping of human-readable aliases to real Google Drive file metadata
        for use in integration tests. Each entry is a dictionary containing 'file_id', 'slug', and 'title'.
"""

import pytest
from flask import current_app

from app import exceptions
from app.controllers.admin_controller import find_unpublished_drive_articles


@pytest.mark.admin_unpublished_posts
@pytest.mark.api
def test_find_unpublished_drive_articles_all_articles_published(
        app,
        session,
        create_blog_post,
        test_drive_file_metadata_map
):
    """Test that when all Drive articles are already in the database, none are returned as unpublished."""
    with app.app_context():
        for metadata in test_drive_file_metadata_map.values():
            create_blog_post(
                title=f'Title for {metadata["slug"]}',
                slug=metadata["slug"],
                html_content=f"Content for {metadata['slug']}",
                drive_file_id=metadata["file_id"],
            )
        session.commit()

        response, status_code = find_unpublished_drive_articles()

        assert status_code == 200
        assert response.json == []


@pytest.mark.admin_unpublished_posts
def test_find_unpublished_drive_articles_empty_database_and_folder(app, session, mocker):
    """Test with no blog posts in the database and no files in Google Drive."""
    with app.app_context():
        # Mock GoogleDriveService.list_folder_contents to return an empty list
        mocker.patch('app.services.google_drive_service.GoogleDriveService.list_folder_contents',
                     return_value=[])
        # Call the function with an empty database and Google Drive folder
        response, status_code = find_unpublished_drive_articles()

        # Expecting 200 with an empty list since there's nothing unpublished
        assert status_code == 200
        assert response.json == []


@pytest.mark.admin_unpublished_posts
def test_find_unpublished_drive_articles_google_drive_api_error(app, session, mocker):
    """Test handling of a general Google Drive API error."""
    with app.app_context():
        # Mock GoogleDriveService to raise a GoogleDriveAPIError
        mocker.patch('app.services.google_drive_service.GoogleDriveService.list_folder_contents',
                     side_effect=exceptions.GoogleDriveAPIError("Google Drive API error"))

        # Call the function, expecting an error response
        response, status_code = find_unpublished_drive_articles()

        # Expecting 500 with a message indicating Google Drive API error
        assert status_code == 500
        assert response.json == {'error': 'Google Drive API error'}


@pytest.mark.admin_unpublished_posts
def test_find_unpublished_drive_articles_no_folder_id(app, session):
    """Test the case where Google Drive folder ID is missing in the config."""
    with app.app_context():
        original_config = current_app.config['DRIVE_BLOG_POSTS_FOLDER_ID']
        try:
            current_app.config['DRIVE_BLOG_POSTS_FOLDER_ID'] = None

            response, status_code = find_unpublished_drive_articles()

            assert status_code == 500
            assert response.json == {
                'error': 'Google Drive folder ID is missing in the configuration'}
        finally:
            current_app.config[
                'DRIVE_BLOG_POSTS_FOLDER_ID'] = original_config  # Restore original config.


@pytest.mark.admin_unpublished_posts
def test_find_unpublished_drive_articles_permission_error(app, session, mocker):
    """Test handling of a Google Drive permission error."""
    with app.app_context():
        # Mock GoogleDriveService to raise a GoogleDrivePermissionError
        mocker.patch('app.services.google_drive_service.GoogleDriveService.list_folder_contents',
                     side_effect=exceptions.GoogleDrivePermissionError(
                         "Insufficient permissions for Google Drive access"))

        # Call the function, expecting a permission error response
        response, status_code = find_unpublished_drive_articles()

        # Expecting 403 with a message indicating insufficient permissions
        assert status_code == 403
        assert response.json == {'error': 'Insufficient permissions for Google Drive access'}


@pytest.mark.admin_unpublished_posts
@pytest.mark.api
def test_find_unpublished_drive_articles_success(app, session, create_blog_post, test_drive_file_metadata_map):
    """
    Test finding missing articles:
    - Stage 1: Insert one article, expect the other in the response.
    - Stage 2: Insert both, expect neither in the response.
    Ignore unrelated entries on Google Drive.
    """
    real_metadata = test_drive_file_metadata_map["design_principles"]
    another_metadata = test_drive_file_metadata_map["value_objects"]

    with app.app_context():
        # Stage 1: Insert only the first article into the DB
        create_blog_post(
            title='Title 1`',
            slug=real_metadata["slug"],
            html_content="<p>Sample content for design principles article.</p>",
            drive_file_id=real_metadata["file_id"],
        )
        session.commit()

        response, status_code = find_unpublished_drive_articles()
        assert status_code == 200

        returned_slugs = [item["slug"] for item in response.json]

        assert another_metadata["slug"] in returned_slugs
        assert real_metadata["slug"] not in returned_slugs

        # Stage 2: Insert the second article too
        create_blog_post(
            title='Another Title',
            slug=another_metadata["slug"],
            html_content="<p>Sample content for value objects article.</p>",
            drive_file_id=another_metadata["file_id"],
        )
        session.commit()

        response, status_code = find_unpublished_drive_articles()
        assert status_code == 200

        returned_slugs = [item["slug"] for item in response.json]

        assert real_metadata["slug"] not in returned_slugs
        assert another_metadata["slug"] not in returned_slugs
