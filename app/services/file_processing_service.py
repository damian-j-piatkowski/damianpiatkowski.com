"""Service for processing blog post files from Google Drive.

This module handles the complete flow of transforming Google Drive documents into blog posts:
    1. Retrieves markdown content from Google Drive
    2. Converts markdown to HTML
    3. Sanitizes HTML content
    4. Persists the blog post in the database

The module provides a single entry point through the process_file function, which
orchestrates all these steps while providing proper error handling and logging.

Typical usage example:
    try:
        blog_post = process_file(
            file_id="1234567890",
            title="My Blog Post",
            slug="my-blog-post"
        )
        print(f"Successfully created blog post: {blog_post.title}")
    except ValueError as e:
        print(f"File not found: {e}")
    except PermissionError as e:
        print(f"Permission denied: {e}")

Attributes:
    logger: Logger instance for this module.
"""

import logging

from app.domain.blog_post import BlogPost
from app.exceptions import BlogPostDuplicateError
from app.exceptions import GoogleDriveFileNotFoundError, GoogleDrivePermissionError
from app.services.blog_service import save_blog_post
from app.services.google_drive_service import GoogleDriveService
from app.services.sanitization_service import sanitize_html

logger = logging.getLogger(__name__)


from app.services.formatting_service import convert_markdown_to_html

def process_file(file_id: str, title: str, slug: str) -> BlogPost:
    """Processes a single file: reads from Google Drive, converts to HTML, sanitizes content, and saves as a blog post.

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

        # Step 1: Read markdown content from Google Drive
        logger.info(f"Reading file with ID {file_id} from Google Drive.")
        markdown_content = google_drive_service.read_file(file_id)

        # Step 2: Convert markdown to HTML
        logger.info(f"Converting markdown to HTML for file ID {file_id}.")
        html_content = convert_markdown_to_html(markdown_content)

        # Step 3: Sanitize HTML content
        logger.info(f"Sanitizing content for file ID {file_id}.")
        sanitized_content = sanitize_html(html_content)

        # Step 4: Save the blog post
        logger.info(f"Saving blog post with title: {title}, slug: {slug}.")
        blog_post = save_blog_post({
            "title": title,
            "slug": slug,
            "html_content": sanitized_content,
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
