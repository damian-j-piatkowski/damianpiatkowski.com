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
        - test_process_file_malformed_metadata:
            Verifies ValueError is raised when the file metadata is malformed.
        - test_process_file_missing_delimiter:
            Verifies ValueError is raised when the metadata block is missing a delimiter.
        - test_process_file_missing_required_metadata:
            Verifies ValueError is raised when required metadata fields are missing.
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
    - test_drive_file_metadata_map: Provides a mapping of human-readable aliases to real Google Drive file metadata
        for use in integration tests. Each entry is a dictionary containing 'file_id', 'slug', and 'title'.
"""

import pytest

from app.exceptions import GoogleDriveFileNotFoundError, GoogleDrivePermissionError, BlogPostDuplicateError
from app.models.repositories.blog_post_repository import BlogPostRepository
from app.services.file_processing_service import process_file

RETURN_MARKDOWN = (
    "Title: Test Post\n"
    "Categories: New\n"
    "Meta Description: A description.\n"
    "Keywords: test\n\n"
    "+++\n\n"
    "This is a mock file content body for testing."
)


@pytest.mark.admin_upload_blog_posts
class TestProcessFileMockedAPI:
    """Integration tests for process_file using mocked Google Drive service.

    These tests simulate expected and exceptional behaviors in isolation by mocking
    Google Drive interactions. They verify correct exception handling, duplicate detection,
    and successful blog post saving.
    """

    def test_process_file_duplicate_error(self, mock_google_drive_service, test_drive_file_metadata_map, session):
        """Tests the case where a duplicate blog post is detected."""
        file_data = test_drive_file_metadata_map["markdown_to_html"]

        # First creation (should succeed)
        process_file(file_data['file_id'], file_data['slug'])

        # Simulate a second file read with the same metadata to trigger duplicate error
        mock_google_drive_service.read_file.return_value = RETURN_MARKDOWN

        with pytest.raises(BlogPostDuplicateError, match="drive_file_id.*already exists"):
            process_file(file_data['file_id'], file_data['slug'])

    def test_process_file_file_not_found(self, mock_google_drive_service, test_drive_file_metadata_map):
        """Tests the case where the file is not found on Google Drive."""
        file_data = test_drive_file_metadata_map["markdown_to_html"]
        mock_google_drive_service.read_file.side_effect = GoogleDriveFileNotFoundError("File not found")
        with pytest.raises(ValueError, match="File not found on Google Drive"):
            process_file(file_data['file_id'], file_data['slug'])

    def test_process_file_malformed_metadata(self, mock_google_drive_service, test_drive_file_metadata_map):
        """Tests that a malformed metadata line causes ValueError."""
        file_data = test_drive_file_metadata_map["markdown_to_html"]
        mock_google_drive_service.read_file.return_value = (
            "Title=Broken Format\n"
            "Categories: Testing\n"
            "Meta Description: Fine.\n"
            "Keywords: test\n\n"
            "+++"
            "\nBody here."
        )
        match_line = ("File is malformed or missing required metadata: "
                      "Malformed metadata line: 'Title=Broken Format'")
        with pytest.raises(ValueError, match=match_line):
            process_file(file_data['file_id'], file_data['slug'])

    def test_process_file_missing_delimiter(self, mock_google_drive_service, test_drive_file_metadata_map):
        """Tests that absence of delimiter raises ValueError."""
        file_data = test_drive_file_metadata_map["markdown_to_html"]
        mock_google_drive_service.read_file.return_value = (
            "Title: No Delimiter\n"
            "Categories: Example\n"
            "Meta Description: Missing delimiter.\n"
            "Keywords: example\n\n"
            "# No separator used here"
        )
        match_line = (
            r"File is malformed or missing required metadata: "
            r"Expected metadata block followed by '\+\+\+' delimiter."
        )
        with pytest.raises(ValueError, match=match_line):
            process_file(file_data['file_id'], file_data['slug'])

    def test_process_file_missing_required_metadata(self, mock_google_drive_service, test_drive_file_metadata_map):
        """Tests that missing required metadata fields raise ValueError."""
        file_data = test_drive_file_metadata_map["markdown_to_html"]
        mock_google_drive_service.read_file.return_value = (
            "Title: Incomplete Post\n"
            "Meta Description: Oops\n\n"
            "+++\nSome body text"
        )
        match_line = (".*File is malformed or missing required metadata: "
                      "Missing required metadata fields: categories, keywords")
        with pytest.raises(ValueError, match=match_line):
            process_file(file_data['file_id'], file_data['slug'])

    def test_process_file_permission_error(self, mock_google_drive_service, test_drive_file_metadata_map):
        """Tests the case where there is a permission error on Google Drive."""
        file_data = test_drive_file_metadata_map["markdown_to_html"]
        mock_google_drive_service.read_file.side_effect = GoogleDrivePermissionError("Permission denied")
        with pytest.raises(PermissionError, match="Permission denied on Google Drive"):
            process_file(file_data['file_id'], file_data['slug'])

    def test_process_file_success(self, mock_google_drive_service, test_drive_file_metadata_map, app, session):
        """Tests the happy path of processing a blog post file."""
        file_data = test_drive_file_metadata_map["markdown_to_html"]
        mock_google_drive_service.read_file.return_value = RETURN_MARKDOWN
        process_file(file_id=file_data['file_id'], slug=file_data['slug'])

        repo = BlogPostRepository(session)
        saved_post = repo.fetch_blog_post_by_slug(file_data['slug'])
        assert saved_post is not None
        assert saved_post.title == 'Test Post'
        assert saved_post.slug == file_data['slug']
        assert saved_post.html_content == "<p>This is a mock file content body for testing.</p>"
        assert saved_post.drive_file_id == file_data['file_id']
        assert saved_post.categories == ['New']
        assert saved_post.meta_description == 'A description.'
        assert saved_post.keywords == ['test']
        assert saved_post.read_time_minutes == 1
        assert saved_post.created_at is not None

    def test_process_file_unexpected_error(self, mock_google_drive_service, test_drive_file_metadata_map, monkeypatch):
        """Tests the case where an unexpected error occurs during saving."""
        file_data = test_drive_file_metadata_map["markdown_to_html"]
        mock_google_drive_service.read_file.return_value = RETURN_MARKDOWN

        def raise_unexpected_error():
            raise Exception("Unexpected error")

        monkeypatch.setattr("app.services.file_processing_service.save_blog_post", raise_unexpected_error)

        with pytest.raises(RuntimeError, match="Unexpected error occurred"):
            process_file(file_data['file_id'], file_data['slug'])


@pytest.mark.admin_upload_blog_posts
@pytest.mark.api
class TestProcessFileRealDriveAPI:
    """Integration tests for process_file using the real Google Drive API.

    These tests validate actual interactions with Google Drive and database integration,
    including duplicate handling, permission issues, and successful processing of real files.
    """

    def test_duplicate_blog_post(self, app, session, test_drive_file_metadata_map):
        """Tests that processing the same file twice results in a duplicate error."""
        metadata = test_drive_file_metadata_map["design_principles"]
        process_file(**metadata)
        with pytest.raises(BlogPostDuplicateError, match="drive_file_id.*already exists"):
            process_file(**metadata)

    def test_duplicate_slug_raises_duplicate_error(self, app, session, test_drive_file_metadata_map):
        """Tests that using the same slug with a different file raises a duplicate error."""
        first = test_drive_file_metadata_map["design_principles"]
        second = test_drive_file_metadata_map["value_objects"]

        process_file(**first)

        duplicate_slug_metadata = second.copy()
        duplicate_slug_metadata["slug"] = first["slug"]

        with pytest.raises(BlogPostDuplicateError, match="slug.*already exists"):
            process_file(**duplicate_slug_metadata)

    def test_duplicate_title_raises_duplicate_error(self, app, session, test_drive_file_metadata_map):
        """Tests that using the same title with a different file raises a duplicate error.

        Prerequisite: The 'value-objects' file needs to have the same title assigned in the metadata block
        as the 'design-principles' file.
        """
        process_file(**test_drive_file_metadata_map["design_principles"])
        with pytest.raises(BlogPostDuplicateError, match="title.*already exists"):
            process_file(**test_drive_file_metadata_map["value_objects"])

    def test_file_not_found_error(self, app):
        """Tests handling of non-existent file IDs."""
        fake_file_id = "nonexistent123abc"
        slug = "missing-file"
        with pytest.raises(ValueError, match="File not found on Google Drive"):
            process_file(fake_file_id, slug)

    def test_process_file_real_drive_not_found_due_to_missing_permission(self, app, test_drive_file_metadata_map):
        """Tests processing a file that is not shared with the bot account, expecting a 404."""
        restricted = test_drive_file_metadata_map["restricted"]
        with pytest.raises(ValueError) as exc_info:
            process_file(**restricted)
        assert "File not found on Google Drive" in str(exc_info.value)

    def test_process_file_real_drive_success(self, app, session, test_drive_file_metadata_map):
        """Tests processing a real Google Drive file via the actual API."""
        metadata = test_drive_file_metadata_map["design_principles"]
        blog_post = process_file(**metadata)

        assert blog_post.slug == metadata["slug"]
        assert blog_post.title == "Six Essential Object-Oriented Design Principles from Matthias Noback's \"Object Design Style Guide\""
        assert blog_post.keywords == ['object-oriented design principles', 'matthias noback',
                                      'object design style guide', 'python design patterns',
                                      'composition over inheritance', 'named constructors python',
                                      'code maintainability', 'clean architecture python',
                                      'object-oriented programming tips', 'design principles for beginners',
                                      'class responsibility assignment', 'domain modeling techniques']
        assert blog_post.meta_description == (
            "Discover six essential object-oriented design principles from "
            "Matthias Noback's 'Object Design Style Guide'—timeless strategies for writing clean, maintainable "
            "code across any programming language, illustrated with Python examples.")
        assert blog_post.drive_file_id == metadata["file_id"]
        assert isinstance(blog_post.html_content, str)
        assert len(blog_post.html_content.strip()) > 0
        assert blog_post.categories == ['Design', 'Python', 'Object-Oriented Programming']
        assert blog_post.read_time_minutes > 10
        assert blog_post.created_at is not None

    def test_unexpected_error_during_sanitization(self, mock_google_drive_service, test_drive_file_metadata_map,
                                                  monkeypatch):
        """Test unexpected error raised from sanitize_html is wrapped in RuntimeError."""
        metadata = test_drive_file_metadata_map["design_principles"]
        mock_google_drive_service.read_file.return_value = RETURN_MARKDOWN

        def raise_unexpected_error():
            raise Exception("Boom during sanitization")

        monkeypatch.setattr("app.services.file_processing_service.sanitize_html", raise_unexpected_error)

        with pytest.raises(RuntimeError, match="Unexpected error occurred"):
            process_file(**metadata)
