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
"""

from flask import current_app

from app import exceptions
from app.controllers.admin_controller import find_unpublished_drive_articles


def test_find_unpublished_drive_articles_all_articles_published(app, session, create_blog_post):
    """Test when all Google Drive articles are already published in the database."""
    with app.app_context():
        # Insert both articles that are in Google Drive folder into the database
        create_blog_post(
            title="01_six_essential_object_oriented_design_principles_from_matthias_"
                  "nobacks_object_design_style_guide",
            content="Content about design principles",
            url="post-1"
        )
        create_blog_post(
            title="02_value_objects",
            content="Content about value objects",
            url="post-2"
        )
        session.commit()

        # Call the function, expecting no missing articles as all are published
        response, status_code = find_unpublished_drive_articles()

        # Expecting 200 with an empty list since all articles are published
        assert status_code == 200
        assert response.json == []


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


def test_find_unpublished_drive_articles_success(app, session, create_blog_post):
    """Test finding missing articles when some are unpublished in Google Drive."""
    with app.app_context():
        # Insert a published article into the database with normalized title
        #
        # Google Drive Test Folder Contents:
        # - "01_six_essential_object_oriented_design_principles_from_matthias_"
        #    "nobacks_object_design_style_guide"
        # - "02_value_objects"
        #
        # After normalization:
        # - "six_essential_object_oriented_design_principles_from_matthias_"
        #    "nobacks_object_design_style_guide"
        # - "value_objects"
        #
        # In this test, we simulate that only the first article is published
        # in the database, so we expect the response to contain only the
        # normalized title of the second article.

        create_blog_post(
            title="01_six_essential_object_oriented_design_principles_from_matthias_"
                  "nobacks_object_design_style_guide",
            content="Content about design principles",
            url="post-1"
        )
        session.commit()

        # Call the actual find_unpublished_drive_articles controller function
        response, status_code = find_unpublished_drive_articles()

        # Expected output with exact id and title match
        expected_response = [
            {"id": "187rlFKQsACliz_ta-niIgK9ZDOwsR9a3YmfrkbX_R1E", "title": "value_objects"}
        ]

        assert status_code == 200
        assert response.json == expected_response
