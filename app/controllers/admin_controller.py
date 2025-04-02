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

from flask import current_app
from flask import jsonify

from app import exceptions
from app.models.data_schemas.blog_post_schema import BlogPostSchema
from app.models.data_schemas.log_schema import LogSchema
from app.services.blog_service import fetch_all_blog_posts
from app.services.file_processing_service import process_file
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


def upload_blog_posts_from_drive(files: List[Dict[str, str]]) -> Tuple:
    """Uploads blog posts from Google Drive using provided file IDs and slugs.

    Args:
        files (List[Dict[str, str]]): A list of dictionaries, each containing:
            - "id" (str): The Google Drive file ID.
            - "slug" (str): The slug to assign to the blog post.

    Returns:
        Tuple[Response, int]: A tuple containing:
            - A dictionary response, formatted as:
                - {"error": "No files provided"} if the input is invalid.
                - {"success": [...], "errors": [...]}:
                    - "success" contains a list of serialized blog post data for successfully
                        processed files.
                    - "errors" contains a list of dictionaries describing issues with individual
                        files.
            - An HTTP status code indicating the result:
                - 400 if no files are provided or none are valid for processing.
                - 201 if all blog posts are successfully created.
                - 207 if some blog posts are successfully created and there are errors.
                - 500 for unexpected critical errors during processing.

    Raises:
        RuntimeError: For critical failures during blog post processing.

    Examples:
        Success Response:
        {
            "success": [
                {
                    "slug": "example-blog-post",
                    "content": "...",
                    "drive_file_id": "12345",
                    "created_at": "2024-12-02T12:00:00"
                }
            ],
            "errors": []
        }

        Mixed Response (Success and Errors):
        {
            "success": [
                {
                    "slug": "example-blog-post",
                    "content": "...",
                    "drive_file_id": "12345",
                    "created_at": "2024-12-02T12:00:00"
                }
            ],
            "errors": [
                {"file_id": "67890", "error": "File not found"}
            ]
        }
    """
    if not files:
        return jsonify({"error": "No files provided"}), 400

    response_data = {"success": [], "errors": []}
    schema = BlogPostSchema()

    for file in files:
        file_id = file.get("id")
        slug = file.get("slug")  # Using "slug" instead of "title"

        if not file_id or not slug:
            response_data["errors"].append({"file_id": file_id, "error": "Missing required fields"})
            continue

        try:
            blog_post = process_file(file_id, slug)  # Ensure this returns a `BlogPost` object

            serialized_post = schema.dump(blog_post)  # Serialize the BlogPost object
            response_data["success"].append(serialized_post)

        except ValueError as ve:
            response_data["errors"].append({"file_id": file_id, "error": str(ve)})
        except PermissionError as pe:
            response_data["errors"].append(
                {"file_id": file_id, "error": "Permission denied on Google Drive"}
            )
            logger.error(f"Permission error for file ID {file_id}: {pe}")
        except Exception as e:
            response_data["errors"].append({"file_id": file_id, "error": "Unexpected error occurred."})
            logger.error(f"Critical exception for file ID {file_id}: {e}")
            break  # Stop processing further files in case of a critical failure

    # Determine status code
    if any(error["error"] == "Unexpected error occurred." for error in response_data["errors"]):
        return jsonify(response_data), 500  # Critical failure
    elif not response_data["success"] and response_data["errors"]:
        return jsonify(response_data), 400  # All errors, no success
    elif response_data["success"] and response_data["errors"]:
        return jsonify(response_data), 207  # Mixed results
    elif response_data["success"]:
        return jsonify(response_data), 201  # All successful

    return jsonify(response_data), 400  # Fallback case

