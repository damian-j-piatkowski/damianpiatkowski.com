"""
Controller for handling blog post retrieval.

This module provides an endpoint for fetching paginated blog posts.
"""

from flask import jsonify, current_app, request
from app.models.data_schemas.blog_post_schema import BlogPostSchema
from app.services.blog_service import get_paginated_blog_posts


def get_paginated_posts(page: int, per_page: int):
    """Fetch paginated blog posts and return them as JSON.

    Args:
        page (int): The current page number.
        per_page (int): The number of posts per page.

    Returns:
        tuple[Response, int]: JSON response containing paginated blog posts and HTTP status code.

    Example:
        - GET `/blog?page=1&per_page=10`
        - Response:
          ```json
          {
              "posts": [...],
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
