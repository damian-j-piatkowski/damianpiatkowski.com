import pytest

from app.exceptions import GoogleDriveFileNotFoundError, GoogleDrivePermissionError
from app.models.repositories.blog_post_repository import BlogPostRepository
from app.services.file_processing_service import process_file


@pytest.mark.admin_upload_post
class TestProcessFileMockedAPI:

    def test_process_file_success(self, mock_google_drive_service, valid_file_data, app, session):
        """Test the happy path of processing a blog post file."""
        mock_google_drive_service.read_file.return_value = "This is a mock file content"

        success, message = process_file(
            file_id=valid_file_data['file_id'],
            title=valid_file_data['title'],
            slug=valid_file_data['slug']
        )

        assert success is True
        expected_message = ("Successfully processed blog post: title='Test Blog Post', slug='test-blog-post', "
                            "drive_file_id='12345'. Preview: This is a mock file content")
        assert expected_message in message
        assert valid_file_data['slug'] in message

        repo = BlogPostRepository(session)
        saved_post = repo.fetch_blog_post_by_slug(valid_file_data['slug'])

        assert saved_post is not None
        assert saved_post.title == valid_file_data['title']
        assert saved_post.slug == valid_file_data['slug']
        assert saved_post.content == "This is a mock file content"
        assert saved_post.drive_file_id == valid_file_data['file_id']
        assert saved_post.created_at is not None

    def test_process_file_file_not_found(self, mock_google_drive_service, valid_file_data):
        """Test the case where the file is not found on Google Drive."""
        mock_google_drive_service.read_file.side_effect = GoogleDriveFileNotFoundError("File not found")

        with pytest.raises(ValueError, match="File not found on Google Drive"):
            process_file(valid_file_data['file_id'], valid_file_data['title'], valid_file_data['slug'])

    def test_process_file_duplicate_error(self, mock_google_drive_service, valid_file_data, session):
        """Test the case where a duplicate blog post is detected."""
        # First save a blog post to trigger a duplicate
        process_file(valid_file_data['file_id'], valid_file_data['title'], valid_file_data['slug'])

        mock_google_drive_service.read_file.return_value = "This is a mock file content"

        success, message = process_file(
            valid_file_data['file_id'],
            valid_file_data['title'],
            valid_file_data['slug']
        )

        assert success is False
        assert "Duplicate blog post: drive_file_id '12345' already exists." in message

    def test_process_file_permission_error(self, mock_google_drive_service, valid_file_data):
        """Test the case where there is a permission error on Google Drive."""
        mock_google_drive_service.read_file.side_effect = GoogleDrivePermissionError("Permission denied")

        with pytest.raises(PermissionError, match="Permission denied on Google Drive"):
            process_file(valid_file_data['file_id'], valid_file_data['title'], valid_file_data['slug'])

    def test_process_file_unexpected_error(self, mock_google_drive_service, valid_file_data, monkeypatch):
        """Test the case where an unexpected error occurs during saving."""
        mock_google_drive_service.read_file.return_value = "This is a mock file content"

        def raise_unexpected_error(*args, **kwargs):
            raise Exception("Unexpected error")

        monkeypatch.setattr("app.services.file_processing_service.save_blog_post", raise_unexpected_error)

        with pytest.raises(RuntimeError, match="Unexpected error occurred"):
            process_file(valid_file_data['file_id'], valid_file_data['title'], valid_file_data['slug'])


@pytest.mark.admin_upload_post
@pytest.mark.api
class TestProcessFileWithRealDriveAPI:
    def test_process_file_real_drive_success(
            self,
            app,
            session,
            real_drive_file_metadata,
    ):
        """Test processing a real Google Drive file via the actual API."""
        success, message = process_file(**real_drive_file_metadata)

        assert success is True
        assert "Successfully processed blog post" in message
        assert f"title='{real_drive_file_metadata['title']}'" in message
        assert f"slug='{real_drive_file_metadata['slug']}'" in message
        assert f"drive_file_id='{real_drive_file_metadata['file_id']}'" in message
        assert "Preview: " in message

        repo = BlogPostRepository(session)
        saved_post = repo.fetch_blog_post_by_slug(real_drive_file_metadata["slug"])

        assert saved_post.title == real_drive_file_metadata["title"]
        assert saved_post.slug == real_drive_file_metadata["slug"]
        assert saved_post.drive_file_id == real_drive_file_metadata["file_id"]
        assert isinstance(saved_post.content, str)
        assert len(saved_post.content.strip()) > 0
        assert saved_post.created_at is not None
