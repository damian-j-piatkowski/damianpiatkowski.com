"""Service for processing blog post files from Google Drive.

This module handles the complete flow of transforming Google Drive documents into blog posts:
    1. Retrieves markdown content from Google Drive
    2. Extracts categories from the first line (if present)
    3. Converts remaining markdown to HTML
    4. Sanitizes HTML content
    5. Persists the blog post in the database

The module provides a single entry point through the process_file function, which
orchestrates all these steps while providing proper error handling and logging.

Categories are expected to be on the first line of the markdown file in the format:
Categories: Python, Web Development, Flask

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
from typing import List, Tuple

from app.domain.blog_post import BlogPost
from app.exceptions import BlogPostDuplicateError
from app.exceptions import GoogleDriveFileNotFoundError, GoogleDrivePermissionError
from app.services.blog_service import save_blog_post
from app.services.formatting_service import convert_markdown_to_html
from app.services.google_drive_service import GoogleDriveService
from app.services.sanitization_service import sanitize_html

logger = logging.getLogger(__name__)


def extract_categories_from_markdown(markdown_content: str) -> Tuple[List[str], str]:
    """Extract categories from the first line and return the rest of the content."""
    cleaned = markdown_content.lstrip('\ufeff')

    if '\n' not in cleaned:
        raise ValueError("Markdown must start with 'Categories:' followed by a newline")

    first_line, rest = cleaned.split('\n', 1)

    if not first_line.lower().startswith("categories:"):
        raise ValueError("First line must start with 'Categories:'")

    categories_str = first_line.removeprefix('Categories:').strip()
    categories = [cat.strip() for cat in categories_str.split(',') if cat]
    return categories, rest.lstrip()


def process_file(file_id: str, title: str, slug: str) -> BlogPost:
    """Processes a single file: reads from Google Drive, extracts categories, converts to HTML, sanitizes content, and saves as a blog post.

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

        # Step 2: Extract categories from markdown content
        logger.info(f"Extracting categories from markdown content for file ID {file_id}.")
        categories, cleaned_markdown = extract_categories_from_markdown(markdown_content)

        # Step 3: Convert remaining markdown to HTML
        logger.info(f"Converting markdown to HTML for file ID {file_id}.")
        html_content = convert_markdown_to_html(cleaned_markdown)

        # Step 4: Sanitize HTML content
        logger.info(f"Sanitizing content for file ID {file_id}.")
        sanitized_content = sanitize_html(html_content)

        # Step 5: Save the blog post with categories
        logger.info(f"Saving blog post with title: {title}, slug: {slug}, categories: {categories}.")
        blog_post = save_blog_post({
            "title": title,
            "slug": slug,
            "html_content": sanitized_content,
            "drive_file_id": file_id,
            "categories": categories
        })

        logger.info(
            f"Successfully processed blog post: "
            f"title='{blog_post.title}', slug='{blog_post.slug}', "
            f"drive_file_id='{blog_post.drive_file_id}', categories={blog_post.categories}"
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
