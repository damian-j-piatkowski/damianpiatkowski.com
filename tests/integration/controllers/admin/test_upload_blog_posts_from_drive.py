"""Integration tests for the upload_blog_posts_from_drive_controller controller function.

This module contains integration tests for the `upload_blog_posts_from_drive_controller` function,
which is responsible for uploading blog posts from Google Drive to the database. The tests
verify the function's behavior under various scenarios, including successful uploads,
validation errors, and unexpected issues.

Test Classes and Functions:

    TestUploadBlogPostsMockedAPI:
        - test_upload_blog_posts_from_drive_errors_only
        - test_upload_blog_posts_from_drive_file_not_found
        - test_upload_blog_posts_from_drive_missing_file_id
        - test_upload_blog_posts_from_drive_mixed_results
        - test_upload_blog_posts_from_drive_no_files
        - test_upload_blog_posts_from_drive_success_only
        - test_upload_blog_posts_from_drive_unexpected_error

    TestUploadBlogPostsRealDriveAPI:
        - test_upload_blog_posts_from_drive_with_actual_api
        - test_upload_multiple_blog_posts_with_actual_api

Fixtures:
    - app: Provides the Flask application context for testing.
    - mock_google_drive_service: Mocks the Google Drive service interactions.
    - session: Manages the database session for test data verification.
    - real_drive_file_metadata: Provides metadata for a real file on Google Drive.
    - another_drive_file_metadata: Provides metadata for another real file on Google Drive.
"""

import json
from datetime import datetime, timedelta, timezone
from typing import Dict, Any
from unittest.mock import Mock

import pytest
from dateutil.parser import parse as parse_datetime
from flask import Flask
from freezegun import freeze_time
from sqlalchemy.orm import Session

from app import exceptions
from app.controllers.admin_controller import upload_blog_posts_from_drive
from tests.scenarios.upload_blog_posts_from_drive_controller import (
    errors_only,
    mixed_results,
    successful_only,
    unexpected_error_included
)


class TestUploadBlogPostsMockedAPI:
    @pytest.mark.parametrize("scenario", errors_only.scenarios)
    def test_upload_blog_posts_from_drive_errors_only(
            self, app: Flask, mock_google_drive_service: Mock, session: Session, scenario: Dict[str, Any]
    ):
        """Tests the behavior of uploading blog posts with only errors occurring."""
        with app.app_context():
            mock_google_drive_service.read_file.side_effect = scenario["side_effects"]
            response, status_code = upload_blog_posts_from_drive(scenario["files"])
            assert status_code == scenario["expected_status"]
            assert response.get_json() == scenario["expected_response"]

    def test_upload_blog_posts_from_drive_file_not_found(self, app, mock_google_drive_service):
        """Tests handling of missing file errors."""
        files = [{"id": "non_existent_id", "title": "Non-existent Post"}]
        mock_google_drive_service.read_file.side_effect = exceptions.GoogleDriveFileNotFoundError

        with app.app_context():
            response, status_code = upload_blog_posts_from_drive(files=files)

        assert status_code == 400
        assert response.get_json() == {
            "success": [],
            "errors": [{"file_id": "non_existent_id", "error": "File not found on Google Drive"}],
        }

    def test_upload_blog_posts_from_drive_missing_file_id(self, app):
        """Tests behavior when a file ID is missing in the payload."""
        with app.app_context():
            files = [{"title": "missing_id"}]
            response, status_code = upload_blog_posts_from_drive(files)
            assert status_code == 400
            assert response.get_json() == {
                "success": [],
                "errors": [{"file": {"title": "missing_id"}, "error": "Missing required fields"}],
            }

    @pytest.mark.parametrize("scenario", mixed_results.scenarios)
    def test_upload_blog_posts_from_drive_mixed_results(
            self,
            app: Flask,
            mock_google_drive_service: Mock,
            session,
            scenario: Dict[str, Any],
    ):
        """Tests the behavior of uploading blog posts when both success and error cases occur."""
        with app.app_context():
            mock_google_drive_service.read_file.side_effect = scenario["side_effects"]
            response, status_code = upload_blog_posts_from_drive(scenario["files"])
            assert status_code == scenario["expected_status"]

            response_json = response.get_json()

            # Validate created_at fields and remove them before comparison
            for success_item in response_json.get("success", []):
                created_at = success_item.pop("created_at", None)
                assert created_at is not None, "created_at is missing from success item"

                # Parse with custom format and attach UTC timezone
                parsed = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                assert isinstance(parsed, datetime)

                # Check that it's within 1 minute of now (UTC)
                now = datetime.now(timezone.utc)
                delta = timedelta(minutes=1)
                assert now - delta <= parsed <= now + delta, f"created_at too far from current time: {created_at}"

            # Final comparison without created_at fields
            assert response_json == scenario["expected_response"]

    def test_upload_blog_posts_from_drive_no_files(self, app):
        """Tests validation when no files are provided."""
        with app.app_context():
            response, status_code = upload_blog_posts_from_drive([])
            assert status_code == 400
            assert response.get_json() == {"error": "No files provided"}

    @pytest.mark.parametrize("scenario", successful_only.scenarios)
    @freeze_time("2024-12-04 14:18:16")
    def test_upload_blog_posts_from_drive_success_only(
            self, app: Flask, mock_google_drive_service: Mock, session: Session, scenario: Dict[str, Any]
    ):
        """Tests the behavior of uploading blog posts with only successful results."""
        with app.app_context():
            mock_google_drive_service.read_file.side_effect = scenario["side_effects"]
            response, status_code = upload_blog_posts_from_drive(scenario["files"])
            assert status_code == scenario["expected_status"]
            assert response == scenario["expected_response"]

    @pytest.mark.parametrize("scenario", unexpected_error_included.scenarios)
    @freeze_time("2024-12-04 14:18:16")
    def test_upload_blog_posts_from_drive_unexpected_error(
            self, app: Flask, mock_google_drive_service: Mock, session: Session, scenario: Dict[str, Any]
    ):
        """Tests handling of unexpected errors during the upload of blog posts from Google Drive."""
        with app.app_context():
            mock_google_drive_service.read_file.side_effect = scenario["side_effects"]
            response, status_code = upload_blog_posts_from_drive(scenario["files"])
            assert status_code == scenario["expected_status"]
            assert response == scenario["expected_response"]


@pytest.mark.api
class TestUploadBlogPostsRealDriveAPI:
    def test_upload_blog_posts_from_drive_with_actual_api(
            self, app, google_drive_service_fixture, session, real_drive_file_metadata
    ):
        """Tests uploading blog posts using the actual Google Drive API."""
        with app.app_context():
            file_id = real_drive_file_metadata["file_id"]
            title = real_drive_file_metadata["title"]
            slug = real_drive_file_metadata["slug"]

            files = [{"id": file_id, "title": title, "slug": slug}]
            response, status_code = upload_blog_posts_from_drive(files)
            response_data = json.loads(response.get_data(as_text=True))

            assert status_code == 201
            assert len(response_data["success"]) == len(files)

            uploaded_post = response_data["success"][0]
            assert uploaded_post["drive_file_id"] == file_id
            assert uploaded_post["title"] == title
            assert uploaded_post["slug"] == slug
            assert "content" in uploaded_post and uploaded_post["content"]

            from app.models.tables.blog_post import blog_posts
            saved_post = session.query(blog_posts).filter_by(drive_file_id=file_id).one_or_none()
            assert saved_post is not None
            assert saved_post.title == title
            assert saved_post.slug == slug
            assert saved_post.content

    def test_upload_multiple_blog_posts_with_actual_api(
            self, app, google_drive_service_fixture, session, real_drive_file_metadata, another_drive_file_metadata
    ):
        """Tests uploading two blog posts using the actual Google Drive API."""
        with app.app_context():
            files = [
                {
                    "id": real_drive_file_metadata["file_id"],
                    "title": real_drive_file_metadata["title"],
                    "slug": real_drive_file_metadata["slug"],
                },
                {
                    "id": another_drive_file_metadata["file_id"],
                    "title": another_drive_file_metadata["title"],
                    "slug": another_drive_file_metadata["slug"],
                },
            ]

            response, status_code = upload_blog_posts_from_drive(files)
            response_data = json.loads(response.get_data(as_text=True))

            assert status_code == 201
            assert len(response_data["success"]) == 2
            assert response_data["errors"] == []

            max_trimmed_length = 200

            for uploaded_post in response_data["success"]:
                assert "content" in uploaded_post
                assert len(uploaded_post["content"]) == max_trimmed_length + 3  # +3 for potential ellipsis
                assert uploaded_post["content"].endswith("...") or len(uploaded_post["content"]) <= max_trimmed_length

            uploaded_slugs = {post["slug"] for post in response_data["success"]}
            assert real_drive_file_metadata["slug"] in uploaded_slugs
            assert another_drive_file_metadata["slug"] in uploaded_slugs

            from app.models.tables.blog_post import blog_posts
            for metadata in [real_drive_file_metadata, another_drive_file_metadata]:
                saved_post = session.query(blog_posts).filter_by(drive_file_id=metadata["file_id"]).one_or_none()
                assert saved_post is not None
                assert saved_post.title == metadata["title"]
                assert saved_post.slug == metadata["slug"]
                assert saved_post.content
