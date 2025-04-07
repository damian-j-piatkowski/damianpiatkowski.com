import logging

from app.domain.blog_post import BlogPost
from app.exceptions import BlogPostDuplicateError
from app.exceptions import GoogleDriveFileNotFoundError, GoogleDrivePermissionError
from app.services.blog_service import save_blog_post
from app.services.google_drive_service import GoogleDriveService
from app.services.sanitization_service import sanitize_html

logger = logging.getLogger(__name__)


def process_file(file_id: str, title: str, slug: str) -> BlogPost:
    """Processes a single file: reads from Google Drive, sanitizes content, and saves as a blog post.

    Args:
        file_id (str): ID of the file to process.
        title (str): Title of the blog post.
        slug (str): URL-friendly slug derived from the title.

    Returns:
        BlogPost: The successfully created blog post domain model.

    Raises:
        BlogPostDuplicateError: If the post already exists.
        ValueError: If the file is not found on Google Drive.
        PermissionError: If Drive access is denied.
        RuntimeError: For any unexpected internal error.
    """
    try:
        google_drive_service = GoogleDriveService()

        # Step 1: Read file content from Google Drive
        logger.info(f"Reading file with ID {file_id} from Google Drive.")
        file_content = google_drive_service.read_file(file_id)

        # Step 2: Sanitize content
        logger.info(f"Sanitizing content for file ID {file_id}.")
        sanitized_content = sanitize_html(file_content)

        # Step 3: Save the blog post
        logger.info(f"Saving blog post with title: {title}, slug: {slug}.")
        blog_post = save_blog_post({
            "title": title,
            "slug": slug,
            "content": sanitized_content,
            "drive_file_id": file_id,
        })

        logger.info(
            f"Successfully processed blog post: "
            f"title='{blog_post.title}', slug='{blog_post.slug}', drive_file_id='{blog_post.drive_file_id}'"
        )

        return blog_post

    except BlogPostDuplicateError as e:
        logger.warning(
            f"Duplicate blog post detected: {e.message} (field: {e.field_name}, value: {e.field_value})"
        )
        raise

    except GoogleDriveFileNotFoundError as e:
        logger.error(f"File not found for file ID {file_id}: {str(e)}")
        raise ValueError("File not found on Google Drive")

    except GoogleDrivePermissionError as e:
        logger.error(f"Permission denied for file ID {file_id}: {str(e)}")
        raise PermissionError("Permission denied on Google Drive")

    except Exception as e:
        logger.error(f"Unexpected error for file ID {file_id}: {str(e)}")
        raise RuntimeError("Unexpected error occurred.")
