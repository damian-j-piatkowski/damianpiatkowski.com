"""Service for processing blog post files from Google Drive.

This module handles the complete flow of transforming Google Drive markdown documents into
structured blog posts with SEO metadata and an estimated read time. It performs the following steps:

    1. Retrieves markdown content from Google Drive
    2. Extracts structured metadata from the first block (Title, Categories, Meta Description, Keywords)
    3. Calculates estimated reading time from the markdown body
    4. Converts remaining markdown to HTML
    5. Sanitizes HTML content
    6. Persists the blog post in the database

The metadata block must be present at the top of the markdown file in this format:

Title: Blog Post Title
Categories: Python, Design, Programming
Meta Description: A one-line summary for SEO purposes.
Keywords: keyword1, keyword2, keyword3

Markdown content starts immediately after this block. The read time is calculated using
a simple word count–based heuristic, ignoring markdown formatting, code blocks, and punctuation.
"""

import logging
import math
import re
from typing import Tuple, Dict

from app.domain.blog_post import BlogPost
from app.exceptions import BlogPostDuplicateError
from app.exceptions import GoogleDriveFileNotFoundError, GoogleDrivePermissionError
from app.services.blog_service import save_blog_post
from app.services.formatting_service import convert_markdown_to_html
from app.services.google_drive_service import GoogleDriveService
from app.services.sanitization_service import sanitize_html

logger = logging.getLogger(__name__)


def calculate_read_time_minutes(markdown_body: str, words_per_minute: int = 200) -> int:
    """Estimates read time in minutes based on word count.

    Args:
        markdown_body (str): Markdown content without the metadata block.
        words_per_minute (int): Average reading speed (default: 200 wpm).

    Returns:
        int: Estimated reading time in minutes (minimum of 1).
    """
    # Remove code blocks and formatting to avoid inflating word count
    cleaned = re.sub(r"(```.*?```|`.*?`)", "", markdown_body, flags=re.DOTALL)
    # Strip markdown formatting like headings, links, emphasis, etc.
    cleaned = re.sub(r"[#*_>\[\]()\-!]", " ", cleaned)
    # Normalize whitespace and split to count words
    words = re.findall(r'\b\w+\b', cleaned)
    word_count = len(words)

    return max(1, math.ceil(word_count / words_per_minute))


def extract_metadata_block(markdown_content: str) -> Tuple[Dict[str, str], str]:
    """Extracts metadata block (title, categories, meta description, keywords) and the remaining markdown body.

    Args:
        markdown_content (str): Full markdown content read from file.

    Returns:
        Tuple[Dict[str, str], str]: Metadata dictionary and markdown body.

    Raises:
        ValueError: If required fields are missing or malformed.
    """
    cleaned = markdown_content.lstrip('\ufeff')  # Handle possible BOM
    lines = cleaned.splitlines()
    metadata = {}
    body_lines = []
    in_metadata = True

    for line in lines:
        if in_metadata and ':' in line:
            key, value = line.split(':', 1)
            metadata[key.strip().lower()] = value.strip()
        else:
            in_metadata = False
            body_lines.append(line)

    required_keys = ['title', 'categories', 'meta description', 'keywords']
    missing = [k for k in required_keys if k not in metadata]
    if missing:
        raise ValueError(f"Missing required metadata fields: {', '.join(missing)}")

    metadata['categories'] = [cat.strip() for cat in metadata['categories'].split(',') if cat]
    metadata['keywords'] = [kw.strip() for kw in metadata['keywords'].split(',') if kw]

    return metadata, '\n'.join(body_lines).lstrip()


def process_file(file_id: str, slug: str) -> BlogPost:
    """Processes a file from Google Drive and creates a blog post.

    Extracts structured metadata (title, categories, keywords, meta description)
    from the top of the file, converts the markdown body to sanitized HTML, and
    saves the result in the database with the given slug.

    Args:
        file_id (str): The Google Drive file ID of the markdown document.
        slug (str): The unique slug for the blog post (typically from the Drive file name).

    Returns:
        BlogPost: The successfully created blog post domain model.

    Raises:
        BlogPostDuplicateError: If a post with the same slug or title already exists.
        ValueError: If the file is malformed or required metadata is missing.
        PermissionError: If access to the file is denied.
        RuntimeError: For unexpected errors.
    """
    try:
        google_drive_service = GoogleDriveService()

        logger.info(f"Reading file with ID {file_id} from Google Drive.")
        markdown_content = google_drive_service.read_file(file_id)

        logger.info(f"Extracting metadata from markdown content for file ID {file_id}.")
        metadata, markdown_body = extract_metadata_block(markdown_content)

        logger.info(f"Calculating read time for file ID {file_id}.")
        read_time = calculate_read_time_minutes(markdown_body)

        logger.info(f"Converting markdown to HTML for file ID {file_id}.")
        html_content = convert_markdown_to_html(markdown_body)

        logger.info(f"Sanitizing HTML content for file ID {file_id}.")
        sanitized_content = sanitize_html(html_content)

        logger.info(f"Saving blog post with slug '{slug}' and metadata: {metadata}")
        blog_post = save_blog_post({
            "title": metadata["title"],
            "slug": slug,
            "html_content": sanitized_content,
            "drive_file_id": file_id,
            "categories": metadata["categories"],
            "seo_keywords": metadata["keywords"],
            "meta_description": metadata["meta description"],
            "read_time_minutes": read_time,
        })

        logger.info(f"Successfully saved blog post: {blog_post.title}")
        return blog_post

    except BlogPostDuplicateError as e:
        logger.warning(f"Duplicate blog post: {e.message} (field: {e.field_name}, value: {e.field_value})")
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
