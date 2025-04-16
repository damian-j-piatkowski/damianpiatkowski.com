"""Admin controller for managing unpublished blog posts stored in Google Drive.

This module defines endpoints used by the admin interface to manage blog content sourced from Google Drive.
It facilitates two main operations:

1. Detecting Unpublished Drive Files:
    - Lists files in the configured Google Drive folder and extracts blog slugs and titles.
    - Compares those slugs to blog posts already stored in the database.
    - Returns metadata about files that have not yet been uploaded as blog posts.

2. Uploading New Blog Posts:
    - Accepts a list of Google Drive file metadata (ID, title, slug) selected for upload.
    - Downloads each file, sanitizes and validates the content, and stores it in the database.
    - Provides detailed feedback indicating which uploads were successful, which failed, and why.

Raises:
    RuntimeError: For internal server errors not specific to Google Drive or blog post validation.
    KeyError: If required fields are missing during blog post upload.
    GoogleDriveFileNotFoundError: If a specified Drive file cannot be found.
    GoogleDrivePermissionError: If access to a Drive file is denied.
    GoogleDriveAPIError: For general issues interacting with the Google Drive API.

Notes:
    - This module is only accessible through authenticated admin routes.
    - It assumes a configured Drive folder ID via `DRIVE_BLOG_POSTS_FOLDER_ID` in app config.
    - Drive files must follow naming conventions compatible with slug and title extraction.
"""

import logging
from typing import List, Dict, Tuple

from flask import Response as FlaskResponse
from flask import current_app, jsonify

from app import exceptions
from app.exceptions import BlogPostDuplicateError
from app.models.data_schemas.blog_post_schema import BlogPostSchema
from app.services.blog_service import get_all_blog_post_identifiers
from app.services.file_processing_service import process_file
from app.services.formatting_service import trim_content
from app.services.google_drive_service import GoogleDriveService
from app.services.sanitization_service import extract_slug_and_title

logger = logging.getLogger(__name__)


def find_unpublished_drive_articles() -> Tuple[FlaskResponse, int]:
    """Fetches unpublished articles from Google Drive and compares with database entries.

    This function retrieves a list of blog post files from Google Drive, extracts slugs and titles,
    and compares them with existing blog posts in the database. It returns a list of articles
    that are present in Google Drive but not yet stored in the database.

    Returns:
        Tuple[FlaskResponse, int]: A tuple containing:
            - A JSON response with a list of missing articles, where each item includes:
                - `slug` (str): The slugified version of the file name (used for URLs).
                - `title` (str): The formatted title extracted from the file name.
                - `id` (str): The Google Drive file ID.
            - An HTTP status code.

    Raises:
        GoogleDriveFileNotFoundError: If specific file(s) are not found in Google Drive.
        GoogleDrivePermissionError: If permissions are insufficient for Google Drive access.
        GoogleDriveAPIError: For general Google Drive API failures.
        RuntimeError: For other errors during article comparison.

    Example Response:
        [
            {"slug": "hello-world", "title": "Hello World", "id": "12345"},
            {"slug": "python-for-beginners", "title": "Python For Beginners", "id": "67890"}
        ]
    """
    folder_id = current_app.config.get("DRIVE_BLOG_POSTS_FOLDER_ID")
    if not folder_id:
        logger.error("Google Drive folder ID is missing in the configuration.")
        return jsonify({'error': 'Google Drive folder ID is missing in the configuration'}), 500

    try:
        db_posts = get_all_blog_post_identifiers()
        db_slugs = {post["slug"] for post in db_posts}
        drive_service = GoogleDriveService()
        drive_files = drive_service.list_folder_contents(folder_id)

        drive_slug_map = {}
        for file in drive_files:
            try:
                slug, title = extract_slug_and_title(file['name'])
                drive_slug_map[slug] = (title, file['id'])
            except ValueError:
                logger.warning(f"Skipping invalid file name: {file['name']}")
                continue

        missing_slugs = set(drive_slug_map.keys()) - db_slugs
        missing_articles = [
            {'slug': slug, 'title': drive_slug_map[slug][0], 'id': drive_slug_map[slug][1]}
            for slug in missing_slugs
        ]

        return jsonify(missing_articles), 200

    except exceptions.GoogleDriveFileNotFoundError as e:
        logger.error(f"Google Drive file not found: {e}")
        return jsonify({'error': str(e)}), 404
    except exceptions.GoogleDrivePermissionError as e:
        logger.error(f"Google Drive permission error: {e}")
        return jsonify({'error': str(e)}), 403
    except exceptions.GoogleDriveAPIError as e:
        logger.error(f"Google Drive API error: {e}")
        return jsonify({'error': str(e)}), 500
    except RuntimeError as e:
        logger.error(f"Error in finding unpublished articles: {e}")
        return jsonify({"error": str(e)}), 500


def upload_blog_posts_from_drive(files: List[Dict[str, str]]) -> Tuple[FlaskResponse, int]:
    """Uploads blog posts from Google Drive using provided file IDs, titles, and slugs.

    Args:
        files (List[Dict[str, str]]): A list of dictionaries, each containing:
            - "id" (str): The Google Drive file ID.
            - "title" (str): The title of the blog post.
            - "slug" (str): The slug to assign to the blog post.

    Returns:
        Tuple[FlaskResponse, int]: A tuple containing:
            - A JSON response with:
                - {"error": "No files provided"} if input is empty.
                - {"success": [...], "errors": [...]} if processing was attempted:
                    - "success": list of serialized blog posts that were successfully created.
                    - "errors": list of file-specific error messages (e.g., missing file, duplicate, etc.).
            - HTTP status code:
                - 400 if input is invalid or all posts failed due to non-critical errors.
                - 201 if all posts were successfully processed.
                - 207 if some posts succeeded and others failed.
                - 500 if a critical error occurred and halted processing.

    Raises:
        RuntimeError: For unrecoverable internal issues during processing.

    Notes:
        - Critical errors (e.g. unexpected exceptions) stop further processing.
        - Non-critical errors (e.g. missing file, permission denied) allow processing to continue.
    """
    if not files:
        return jsonify({"error": "No files provided"}), 400

    response_data = {"success": [], "errors": []}
    schema = BlogPostSchema()

    for file in files:
        file_id = file.get("id")
        title = file.get("title")
        slug = file.get("slug")

        if not file_id or not title or not slug:
            response_data["errors"].append({
                "file_id": file.get("id", "unknown"),
                "error": "Missing required fields",
            })
            continue

        try:
            blog_post = process_file(file_id, title, slug)
            serialized_post = schema.dump(blog_post)
            serialized_post["content"] = trim_content(serialized_post.get("content", ""))
            response_data["success"].append(serialized_post)

        except BlogPostDuplicateError as de:
            response_data["errors"].append({
                "file_id": file_id,
                "error": str(de)
            })
        except ValueError as ve:
            response_data["errors"].append({"file_id": file_id, "error": str(ve)})
        except PermissionError as pe:
            response_data["errors"].append({
                "file_id": file_id,
                "error": "Permission denied on Google Drive"
            })
            logger.error(f"Permission error for file ID {file_id}: {pe}")
        except Exception as e:
            error_message = f"{type(e).__name__}: {e}"
            response_data["errors"].append({
                "file_id": file_id,
                "error": f"Unexpected error occurred: {error_message}",
            })
            logger.exception(f"Critical exception for file ID {file_id}")
            break

    has_success = bool(response_data["success"])
    has_errors = bool(response_data["errors"])
    has_critical_error = any(
        "Unexpected error occurred" in err["error"] for err in response_data["errors"]
    )

    if has_critical_error and not has_success:
        return jsonify(response_data), 500
    elif has_critical_error and has_success:
        return jsonify(response_data), 207
    elif has_errors and has_success:
        return jsonify(response_data), 207
    elif has_errors and not has_success:
        return jsonify(response_data), 400
    else:
        return jsonify(response_data), 201
