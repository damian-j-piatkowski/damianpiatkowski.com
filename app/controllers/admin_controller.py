"""Admin controller for handling requests related to logs, blog posts, and Google Drive articles.

This module includes endpoints for:
- Fetching unpublished articles from Google Drive
- Retrieving all logs from the database
- Uploading new blog posts after validation and sanitization

Raises:
    RuntimeError: If there are issues fetching or saving data.
    KeyError: If required blog post fields are missing during upload.

"""

import logging
from typing import List, Dict, Tuple

from flask import Response as FlaskResponse
from flask import current_app
from flask import jsonify
from requests import Response

from app import exceptions
from app.exceptions import BlogPostDuplicateError
from app.models.data_schemas.blog_post_schema import BlogPostSchema
from app.models.data_schemas.log_schema import LogSchema
from app.services.blog_service import fetch_all_blog_posts
from app.services.file_processing_service import process_file
from app.services.formatting_service import trim_content
from app.services.google_drive_service import GoogleDriveService
from app.services.log_service import fetch_all_logs
from app.services.sanitization_service import extract_slug_and_title

logger = logging.getLogger(__name__)


def find_unpublished_drive_articles() -> jsonify:
    """Fetches unpublished articles from Google Drive and compares with database entries.

    This function retrieves a list of blog post files from Google Drive, extracts slugs and titles,
    and compares them with existing blog posts in the database. It returns a list of articles
    that are present in Google Drive but not yet stored in the database.

    Returns:
        jsonify: JSON response containing missing articles, each with:
            - `slug` (str): The slugified version of the file name (used for URLs).
            - `title` (str): The formatted title extracted from the file name.
            - `id` (str): The Google Drive file ID.

    Raises:
        GoogleDriveFileNotFoundError: If specific file(s) are not found in Google Drive.
        GoogleDrivePermissionError: If permissions are insufficient for Google Drive access.
        GoogleDriveAPIError: For general Google Drive API failures.
        RuntimeError: For other errors during article comparison.

    Example Response:
        If some articles are missing from the database:
        ```json
        [
            {"slug": "hello-world", "title": "Hello World", "id": "12345"},
            {"slug": "python-for-beginners", "title": "Python For Beginners", "id": "67890"}
        ]
        ```

        If all Drive articles are already in the database:
        ```json
        []
        ```

        If an error occurs (e.g., missing folder ID):
        ```json
        {"error": "Google Drive folder ID is missing in the configuration"}
        ```
    """
    try:
        # Fetch blog posts from the database and normalize their slugs
        db_posts = fetch_all_blog_posts()
        db_slugs = {post.slug for post in db_posts}  # Now comparing SLUGS, not titles

        # Fetch folder ID from the app configuration
        folder_id = current_app.config.get('DRIVE_BLOG_POSTS_FOLDER_ID')
        if not folder_id:
            current_app.logger.error("Google Drive folder ID is missing in the configuration.")
            return jsonify({'error': 'Google Drive folder ID is missing in the configuration'}), 500

        # Get Google Drive service and list folder contents with IDs
        drive_service = GoogleDriveService()
        drive_files = drive_service.list_folder_contents(folder_id)

        # Extract slugs and titles from file names
        drive_slug_map = {}  # Maps slug -> (title, id)
        for file in drive_files:
            try:
                slug, title = extract_slug_and_title(file['name'])
                drive_slug_map[slug] = (title, file['id'])
            except ValueError:
                # Log and skip invalid filenames
                current_app.logger.warning(f"Skipping invalid file name: {file['name']}")
                continue

        # Find missing articles by comparing slugs (not just titles)
        missing_slugs = set(drive_slug_map.keys()) - db_slugs
        missing_articles = [
            {'slug': slug, 'title': drive_slug_map[slug][0], 'id': drive_slug_map[slug][1]}
            for slug in missing_slugs
        ]

        return jsonify(missing_articles), 200

    except exceptions.GoogleDriveFileNotFoundError as e:
        current_app.logger.error(f"Google Drive file not found: {e}")
        return jsonify({'error': str(e)}), 404
    except exceptions.GoogleDrivePermissionError as e:
        current_app.logger.error(f"Google Drive permission error: {e}")
        return jsonify({'error': str(e)}), 403
    except exceptions.GoogleDriveAPIError as e:
        current_app.logger.error(f"Google Drive API error: {e}")
        return jsonify({'error': str(e)}), 500
    except RuntimeError as e:
        current_app.logger.error(f"Error in finding unpublished articles: {e}")
        return jsonify({"error": str(e)}), 500


def get_logs_data():
    """Fetch logs and serialize them for JSON response."""
    try:
        logs = fetch_all_logs()  # List[Log]
        if not logs:
            current_app.logger.info("No logs found.")
            return jsonify({"message": "No logs found"}), 404

        schema = LogSchema(many=True)  # Instantiate schema for multiple logs
        serialized_logs = schema.dump(logs)  # Serialize the domain objects
        return jsonify(serialized_logs), 200  # Return serialized data with status 200
    except RuntimeError as e:
        current_app.logger.error(f"Failed to retrieve logs: {e}")
        return jsonify({"error": str(e)}), 500  # Return error with status 500


def upload_blog_posts_from_drive(files: List[Dict[str, str]]) -> Tuple[FlaskResponse, int]:
    """Uploads blog posts from Google Drive using provided file IDs, titles, and slugs.

    Args:
        files (List[Dict[str, str]]): A list of dictionaries, each containing:
            - "id" (str): The Google Drive file ID.
            - "title" (str): The title of the blog post.
            - "slug" (str): The slug to assign to the blog post.

    Returns:
        Tuple[Response, int]: A tuple containing:
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

    Example:
        Input:
        [
            {
                "id": "12345",
                "title": "Example Title",
                "slug": "example-title"
            }
        ]

        Response:
        (
            {
                "success": [
                    {
                        "slug": "example-title",
                        "content": "...",
                        "drive_file_id": "12345",
                        "created_at": "2025-04-09 06:54:21"
                    }
                ],
                "errors": []
            },
            201
        )
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
            logger.exception(f"Critical exception for file ID {file_id}")  # Includes traceback
            break  # Critical error halts further processing

    has_success = bool(response_data["success"])
    has_errors = bool(response_data["errors"])
    has_critical_error = any(
        "Unexpected error occurred" in err["error"] for err in response_data["errors"]
    )

    # Determine response code
    if has_critical_error and not has_success:
        return jsonify(response_data), 500  # Full failure due to critical error(s)
    elif has_critical_error and has_success:
        return jsonify(response_data), 207  # Mixed, but critical present — partial success
    elif has_errors and has_success:
        return jsonify(response_data), 207  # Mixed, only non-critical errors
    elif has_errors and not has_success:
        return jsonify(response_data), 400  # All errors, but non-critical
    else:
        return jsonify(response_data), 201  # All good
