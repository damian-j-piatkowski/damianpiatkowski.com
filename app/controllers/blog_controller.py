"""Controller for handling blog post retrieval.

This module provides a function for fetching paginated blog posts.
"""

from flask import Response
from flask import jsonify, current_app

from app.models.data_schemas.blog_post_schema import BlogPostSchema
from app.services.blog_service import get_paginated_blog_posts


def get_paginated_posts(page: int, per_page: int) -> tuple[Response, int]:
    """Handles the retrieval of paginated blog posts and returns a JSON response.

    This function calls the service layer to fetch paginated blog posts and formats
    the result as a JSON response, including the total number of pages.

    Args:
        page (int): The current page number.
        per_page (int): The number of posts per page.

    Returns:
        tuple[Response, int]: A Flask JSON response containing paginated blog posts and
        total pages, along with the corresponding HTTP status code.

    Example:
        - GET `/blog?page=1&per_page=10`
        - Response:
          ```json
          {
              "posts": [
                  {"title": "Post 1", "content": "...", "drive_file_id": "..."},
                  {"title": "Post 2", "content": "...", "drive_file_id": "..."}
              ],
              "total_pages": 5
          }
          ```
    """
    try:
        posts, total_pages = get_paginated_blog_posts(page, per_page)

        if not posts:
            current_app.logger.info("No blog posts found.")
            return jsonify({"message": "No blog posts found"}), 404

        schema = BlogPostSchema(many=True)
        serialized_posts = schema.dump(posts)

        return jsonify({"posts": serialized_posts, "total_pages": total_pages}), 200

    except RuntimeError as e:
        current_app.logger.error(f"Failed to retrieve blog posts: {e}")
        return jsonify({"error": str(e)}), 500  # Internal Server Error
