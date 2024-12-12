import logging

from app.exceptions import GoogleDriveFileNotFoundError, GoogleDrivePermissionError
from app.models.data_schemas.blog_post_schema import BlogPostSchema
from app.services.blog_service import save_blog_post
from app.services.google_drive_service import GoogleDriveService
from app.services.sanitization_service import sanitize_html
from app.exceptions import BlogPostDuplicateError

logger = logging.getLogger(__name__)


def process_file(file_id: str, title: str) -> tuple[bool, str]:
    """
    Processes a single file: reads from Google Drive, sanitizes, and saves as a blog post.

    Args:
        file_id (str): ID of the file to process.
        title (str): Title of the blog post.

    Returns:
        tuple: (success: bool, message: str) where success indicates if the operation succeeded,
               and message contains either the success message or error details.
    """
    try:
        google_drive_service = GoogleDriveService()

        # Step 1: Read file content from Google Drive
        logger.info(f"Reading file with ID {file_id} from Google Drive.")
        file_content = google_drive_service.read_file(file_id)

        # Step 2: Convert and sanitize content
        logger.info(f"Sanitizing content for file ID {file_id}.")
        sanitized_content = sanitize_html(file_content)

        # Step 3: Save the blog post
        logger.info(f"Saving blog post with title: {title}.")
        blog_post = save_blog_post({
            "title": title,
            "content": sanitized_content,
            "drive_file_id": file_id,
        })

        # Return success tuple with serialized blog post
        success_message = f"Blog post successfully processed: {BlogPostSchema().dump(blog_post)}"
        return True, success_message

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


