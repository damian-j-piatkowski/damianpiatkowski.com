"""Integration tests for the process_file function of the file_processing_service module.

This module contains integration tests for the process_file function, which handles reading,
sanitizing, and saving blog post content from Google Drive. The tests are divided into two categories:
mocked interactions and real API interactions. The goal is to verify that process_file behaves correctly
under both expected and error conditions, including handling duplicates, permission issues, and unexpected errors.

Test Classes and Functions:

    TestProcessFileMockedAPI:
        - test_process_file_duplicate_error:
            Verifies proper handling when attempting to save a duplicate blog post.
        - test_process_file_file_not_found:
            Verifies ValueError is raised when the file is not found on Google Drive.
        - test_process_file_permission_error:
            Verifies PermissionError is raised when Drive access is denied.
        - test_process_file_success:
            Verifies the happy path with a successful file read and post save.
        - test_process_file_unexpected_error:
            Verifies unexpected errors during saving are wrapped in RuntimeError.

    TestProcessFileRealDriveAPI:
        - test_duplicate_blog_post:
            Verifies detection of duplicate posts based on file ID.
        - test_duplicate_slug_raises_duplicate_error:
            Verifies detection of duplicate slug with different file.
        - test_duplicate_title_raises_duplicate_error:
            Verifies detection of duplicate title with different file.
        - test_file_not_found_error:
            Verifies handling of non-existent file IDs.
        - test_process_file_real_drive_not_found_due_to_missing_permission:
            Verifies error when processing a file not shared with the bot account.
        - test_process_file_real_drive_success:
            Verifies successful blog post processing using a real Drive file.
        - test_unexpected_error_during_sanitization:
            Verifies unexpected errors during sanitization are wrapped in RuntimeError.

Fixtures:
    - app: Provides a test instance of the Flask application.
    - session: Provides a transactional database session for integration testing.
    - mock_google_drive_service: Mocks Google Drive interactions.
    - real_drive_file_metadata: Provides real file metadata for Drive-based tests.
    - restricted_drive_file_metadata: Provides metadata for a file the bot cannot access.
    - another_drive_file_metadata: Provides a second distinct file for duplicate testing.
"""

import pytest

from app.exceptions import GoogleDriveFileNotFoundError, GoogleDrivePermissionError, BlogPostDuplicateError
from app.models.repositories.blog_post_repository import BlogPostRepository
from app.services.file_processing_service import process_file


@pytest.mark.admin_upload_post
class TestProcessFileMockedAPI:

    def test_process_file_duplicate_error(self, mock_google_drive_service, valid_file_data, session):
        """Test the case where a duplicate blog post is detected."""
        process_file(valid_file_data['file_id'], valid_file_data['title'], valid_file_data['slug'])
        mock_google_drive_service.read_file.return_value = "This is a mock file content"
        with pytest.raises(BlogPostDuplicateError, match="drive_file_id.*already exists"):
            process_file(valid_file_data['file_id'], valid_file_data['title'], valid_file_data['slug'])

    def test_process_file_file_not_found(self, mock_google_drive_service, valid_file_data):
        """Test the case where the file is not found on Google Drive."""
        mock_google_drive_service.read_file.side_effect = GoogleDriveFileNotFoundError("File not found")
        with pytest.raises(ValueError, match="File not found on Google Drive"):
            process_file(valid_file_data['file_id'], valid_file_data['title'], valid_file_data['slug'])

    def test_process_file_permission_error(self, mock_google_drive_service, valid_file_data):
        """Test the case where there is a permission error on Google Drive."""
        mock_google_drive_service.read_file.side_effect = GoogleDrivePermissionError("Permission denied")
        with pytest.raises(PermissionError, match="Permission denied on Google Drive"):
            process_file(valid_file_data['file_id'], valid_file_data['title'], valid_file_data['slug'])

    def test_process_file_success(self, mock_google_drive_service, valid_file_data, app, session):
        """Test the happy path of processing a blog post file."""
        mock_google_drive_service.read_file.return_value = "This is a mock file content"
        process_file(
            file_id=valid_file_data['file_id'],
            title=valid_file_data['title'],
            slug=valid_file_data['slug']
        )
        repo = BlogPostRepository(session)
        saved_post = repo.fetch_blog_post_by_slug(valid_file_data['slug'])
        assert saved_post is not None
        assert saved_post.title == valid_file_data['title']
        assert saved_post.slug == valid_file_data['slug']
        assert saved_post.content == "This is a mock file content"
        assert saved_post.drive_file_id == valid_file_data['file_id']
        assert saved_post.created_at is not None

    def test_process_file_unexpected_error(self, mock_google_drive_service, valid_file_data, monkeypatch):
        """Tests the case where an unexpected error occurs during saving."""
        mock_google_drive_service.read_file.return_value = "This is a mock file content"

        def raise_unexpected_error():
            raise Exception("Unexpected error")

        monkeypatch.setattr("app.services.file_processing_service.save_blog_post", raise_unexpected_error)

        with pytest.raises(RuntimeError, match="Unexpected error occurred"):
            process_file(valid_file_data['file_id'], valid_file_data['title'], valid_file_data['slug'])


@pytest.mark.admin_upload_post
@pytest.mark.api
class TestProcessFileRealDriveAPI:

    def test_duplicate_blog_post(self, app, session, real_drive_file_metadata):
        """Tests that processing the same file twice results in a duplicate error."""
        process_file(**real_drive_file_metadata)
        with pytest.raises(BlogPostDuplicateError, match="drive_file_id.*already exists"):
            process_file(**real_drive_file_metadata)

    def test_duplicate_slug_raises_duplicate_error(self, app, session, real_drive_file_metadata,
                                                   another_drive_file_metadata):
        """Tests that using the same slug with a different file raises a duplicate error."""
        process_file(**real_drive_file_metadata)
        duplicate_slug_metadata = another_drive_file_metadata.copy()
        duplicate_slug_metadata["slug"] = real_drive_file_metadata["slug"]
        with pytest.raises(BlogPostDuplicateError, match="slug.*already exists"):
            process_file(**duplicate_slug_metadata)

    def test_duplicate_title_raises_duplicate_error(self, app, session, real_drive_file_metadata,
                                                    another_drive_file_metadata):
        """Tests that using the same title with a different file raises a duplicate error."""
        process_file(**real_drive_file_metadata)
        duplicate_title_metadata = another_drive_file_metadata.copy()
        duplicate_title_metadata["title"] = real_drive_file_metadata["title"]
        with pytest.raises(BlogPostDuplicateError, match="title.*already exists"):
            process_file(**duplicate_title_metadata)

    def test_file_not_found_error(self, app):
        """Tests handling of non-existent file IDs."""
        fake_file_id = "nonexistent123abc"
        title = "Missing File"
        slug = "missing-file"
        with pytest.raises(ValueError, match="File not found on Google Drive"):
            process_file(fake_file_id, title, slug)

    def test_process_file_real_drive_not_found_due_to_missing_permission(self, app, restricted_drive_file_metadata):
        """Tests processing a file that is not shared with the bot account, expecting a 404."""
        with pytest.raises(ValueError) as exc_info:
            process_file(**restricted_drive_file_metadata)
        assert "File not found on Google Drive" in str(exc_info.value)

    def test_process_file_real_drive_success(self, app, session, real_drive_file_metadata):
        """Tests processing a real Google Drive file via the actual API."""
        blog_post = process_file(**real_drive_file_metadata)
        assert blog_post.title == real_drive_file_metadata["title"]
        assert blog_post.slug == real_drive_file_metadata["slug"]
        assert blog_post.drive_file_id == real_drive_file_metadata["file_id"]
        assert isinstance(blog_post.content, str)
        assert len(blog_post.content.strip()) > 0
        assert blog_post.created_at is not None

    def test_unexpected_error_during_sanitization(self, mock_google_drive_service, real_drive_file_metadata,
                                                  monkeypatch):
        """Test unexpected error raised from sanitize_html is wrapped in RuntimeError."""
        mock_google_drive_service.read_file.return_value = "This is a mock file content"

        def raise_unexpected_error():
            raise Exception("Boom during sanitization")

        monkeypatch.setattr("app.services.file_processing_service.sanitize_html", raise_unexpected_error)

        with pytest.raises(RuntimeError, match="Unexpected error occurred"):
            process_file(**real_drive_file_metadata)
