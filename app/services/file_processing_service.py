import logging

from app.exceptions import BlogPostDuplicateError
from app.exceptions import GoogleDriveFileNotFoundError, GoogleDrivePermissionError
from app.services.blog_service import save_blog_post
from app.services.google_drive_service import GoogleDriveService
from app.services.sanitization_service import sanitize_html

logger = logging.getLogger(__name__)


def process_file(file_id: str, title: str, slug: str) -> tuple[bool, str]:
    """Processes a single file: reads from Google Drive, sanitizes, and saves as a blog post.

    Args:
        file_id (str): ID of the file to process.
        title (str): Title of the blog post.
        slug (str): URL-friendly slug derived from the title.

    Returns:
        tuple: (success: bool, message: str) where success indicates if the operation succeeded,
               and message contains either the success message or error details.
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
            "slug": slug,  # Ensure slug is passed
            "content": sanitized_content,
            "drive_file_id": file_id,
        })

        preview = blog_post.content[:200].replace("\n", " ") + ("..." if len(blog_post.content) > 100 else "")
        message = (
            f"Successfully processed blog post: "
            f"title='{blog_post.title}', slug='{blog_post.slug}', drive_file_id='{blog_post.drive_file_id}'. "
            f"Preview: {preview}"
        )

        logger.info(message)
        return True, message

    except BlogPostDuplicateError as e:
        logger.warning(
            f"Duplicate blog post detected: {e.message} (field: {e.field_name}, value: {e.field_value})")
        return False, f"Duplicate blog post: {e.field_name} '{e.field_value}' already exists."
    except GoogleDriveFileNotFoundError as e:
        logger.error(f"File not found for file ID {file_id}: {str(e)}")
        raise ValueError("File not found on Google Drive")  # Propagate meaningful error
    except GoogleDrivePermissionError as e:
        logger.error(f"Permission denied for file ID {file_id}: {str(e)}")
        raise PermissionError("Permission denied on Google Drive")
    except Exception as e:
        logger.error(f"Unexpected error for file ID {file_id}: {str(e)}")
        raise RuntimeError("Unexpected error occurred.")
