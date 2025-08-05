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
    - test_drive_file_metadata_map: Provides a mapping of human-readable aliases to real Google Drive file metadata
        for use in integration tests. Each entry is a dictionary containing 'file_id', 'slug', and 'title'.
"""

import json
from datetime import datetime, timedelta, timezone
from typing import Dict, Any
from unittest.mock import Mock

import pytest
from flask import Flask
from sqlalchemy.orm import Session

from app import exceptions
from app.controllers.admin_controller import upload_blog_posts_from_drive
from tests.scenarios.upload_blog_posts_from_drive_controller import (
    errors_only,
    mixed_results,
    successful_only,
    unexpected_error_included
)


@pytest.mark.admin_upload_blog_posts
class TestUploadBlogPostsMockedAPI:
    """Integration tests for uploading blog posts using a mocked Google Drive API.

    These tests simulate the interaction with the Google Drive API by mocking the
    API responses. The goal is to validate the handling of blog post uploads without
    relying on an actual Google Drive instance. The tests verify that the system
    behaves as expected when interacting with mocked API responses.
    """

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
        files = [{"id": "non_existent_id", "title": "Non-existent Post", "slug": "non-existent-id"}]
        mock_google_drive_service.read_file.side_effect = exceptions.GoogleDriveFileNotFoundError(
            "Test error: file not found", file_id="non_existent_id"),

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
                "errors": [{"file_id": "unknown", "error": "Missing required fields"}],
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

            # Validate created_at and updated_at fields and remove them before comparison
            for success_item in response_json.get("success", []):
                now = datetime.now(timezone.utc)
                delta = timedelta(minutes=1)

                # created_at
                created_at = success_item.pop("created_at", None)
                assert created_at is not None, "created_at is missing from success item"
                parsed_created = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                assert now - delta <= parsed_created <= now + delta, f"created_at too far from current time: {created_at}"

                # updated_at
                updated_at = success_item.pop("updated_at", None)
                assert updated_at is not None, "updated_at is missing from success item"
                parsed_updated = datetime.strptime(updated_at, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                assert now - delta <= parsed_updated <= now + delta, f"updated_at too far from current time: {updated_at}"

            # Final comparison without created_at/updated_at fields
            assert response_json == scenario["expected_response"]

    def test_upload_blog_posts_from_drive_no_files(self, app):
        """Tests validation when no files are provided."""
        with app.app_context():
            response, status_code = upload_blog_posts_from_drive([])
            assert status_code == 400
            assert response.get_json() == {"error": "No files provided"}

    @pytest.mark.parametrize("scenario", successful_only.scenarios)
    def test_upload_blog_posts_from_drive_success_only(
            self,
            app: Flask,
            mock_google_drive_service: Mock,
            session: Session,
            scenario: Dict[str, Any],
    ):
        """Tests the behavior of uploading blog posts with only successful results."""
        with app.app_context():
            mock_google_drive_service.read_file.side_effect = scenario["side_effects"]
            response, status_code = upload_blog_posts_from_drive(scenario["files"])
            assert status_code == scenario["expected_status"]

            response_json = response.get_json()

            # Validate created_at and updated_at fields and remove them before comparison
            for success_item in response_json.get("success", []):
                # Handle created_at
                created_at = success_item.pop("created_at", None)
                assert created_at is not None, "created_at is missing from success item"

                parsed_created = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                assert isinstance(parsed_created, datetime)

                now = datetime.now(timezone.utc)
                delta = timedelta(minutes=1)
                assert now - delta <= parsed_created <= now + delta, f"created_at too far from current time: {created_at}"

                # Handle updated_at (same logic)
                updated_at = success_item.pop("updated_at", None)
                assert updated_at is not None, "updated_at is missing from success item"

                parsed_updated = datetime.strptime(updated_at, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                assert isinstance(parsed_updated, datetime)
                assert now - delta <= parsed_updated <= now + delta, f"updated_at too far from current time: {updated_at}"

            # Final comparison without created_at fields
            assert response_json == scenario["expected_response"]

    @pytest.mark.parametrize("scenario", unexpected_error_included.scenarios)
    def test_upload_blog_posts_from_drive_unexpected_error(
            self, app: Flask, mock_google_drive_service: Mock, session: Session, scenario: Dict[str, Any]
    ):
        """Tests handling of unexpected errors during the upload of blog posts from Google Drive."""
        with app.app_context():
            mock_google_drive_service.read_file.side_effect = scenario["side_effects"]
            response, status_code = upload_blog_posts_from_drive(scenario["files"])

            assert status_code == scenario["expected_status"]

            response_json = response.get_json()

            # Only validate and strip created_at if there are success items
            for success_item in response_json.get("success", []):
                created_at = success_item.pop("created_at", None)
                assert created_at is not None, "created_at is missing from success item"

                # updated_at
                updated_at = success_item.pop("updated_at", None)
                assert updated_at is not None, "updated_at is missing from success item"

            # Final response comparison (created_at is now removed)
            assert response_json == scenario["expected_response"]


@pytest.mark.api
@pytest.mark.admin_upload_blog_posts
class TestUploadBlogPostsRealDriveAPI:
    """Integration tests for uploading blog posts using the real Google Drive API.

    These tests validate that blog post files retrieved from Google Drive are correctly
    processed, sanitized, stored in the database, and returned in the expected response
    format. Each test exercises the end-to-end flow using actual Drive files configured
    via the test metadata fixture.
    """

    def test_upload_blog_posts_from_drive_with_actual_api(
            self, app, google_drive_service_fixture, session, test_drive_file_metadata_map
    ):
        """Tests uploading a single blog post using the actual Google Drive API."""
        metadata = test_drive_file_metadata_map["design_principles"]

        with app.app_context():
            file_id = metadata["file_id"]
            slug = metadata["slug"]

            files = [{"id": file_id, "slug": slug}]
            response, status_code = upload_blog_posts_from_drive(files)
            response_data = json.loads(response.get_data(as_text=True))

            assert status_code == 201
            assert len(response_data["success"]) == len(files)

            uploaded_post = response_data["success"][0]
            assert uploaded_post["title"] == 'Six Essential Object-Oriented Design Principles from Matthias Noback\'s "Object Design Style Guide"'
            assert uploaded_post["read_time_minutes"] >= 10
            assert uploaded_post["drive_file_id"] == file_id
            assert uploaded_post["slug"] == slug
            assert "html_content" in uploaded_post and uploaded_post["html_content"]

            from app.models.tables.blog_post import blog_posts
            saved_post = session.query(blog_posts).filter_by(drive_file_id=file_id).one_or_none()
            assert saved_post is not None
            assert saved_post.slug == slug
            assert saved_post.html_content

    def test_upload_multiple_blog_posts_with_actual_api(
            self, app, google_drive_service_fixture, session, test_drive_file_metadata_map
    ):
        """Tests uploading two blog posts using the actual Google Drive API."""
        metadata_1 = test_drive_file_metadata_map["design_principles"]
        metadata_2 = test_drive_file_metadata_map["value_objects"]

        with app.app_context():
            files = [
                {"id": metadata_1["file_id"], "slug": metadata_1["slug"]},
                {"id": metadata_2["file_id"], "slug": metadata_2["slug"]},
            ]

            response, status_code = upload_blog_posts_from_drive(files)
            response_data = json.loads(response.get_data(as_text=True))

            assert status_code == 201
            assert len(response_data["success"]) == 2
            assert response_data["errors"] == []

            max_trimmed_length = 200

            for uploaded_post in response_data["success"]:
                assert "html_content" in uploaded_post
                html_content = uploaded_post["html_content"]

                if html_content.endswith("..."):
                    # Account for rstrip() in trim_content function
                    # Length should be <= max_length + 3 (could be less due to rstrip)
                    assert len(html_content) <= max_trimmed_length + 3
                    assert len(html_content) > max_trimmed_length  # But should be more than max_length
                else:
                    assert len(html_content) <= max_trimmed_length

            assert uploaded_post["html_content"].endswith("...") or len(
                    uploaded_post["html_content"]) <= max_trimmed_length

            uploaded_slugs = {post["slug"] for post in response_data["success"]}
            assert metadata_1["slug"] in uploaded_slugs
            assert metadata_2["slug"] in uploaded_slugs

            from app.models.tables.blog_post import blog_posts
            for metadata in [metadata_1, metadata_2]:
                saved_post = session.query(blog_posts).filter_by(drive_file_id=metadata["file_id"]).one_or_none()
                assert saved_post is not None
                assert saved_post.slug == metadata["slug"]
                assert saved_post.html_content
