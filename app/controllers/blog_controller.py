"""Controller for handling blog post retrieval.

This module provides functions for fetching blog posts, including:
    - get_paginated_posts: Retrieves paginated blog posts.
    - get_single_post: Retrieves a single blog post by its slug.
"""

from flask import Response, jsonify, current_app

from app.exceptions import BlogPostNotFoundError
from app.models.data_schemas.blog_post_schema import BlogPostSchema
from app.services.blog_service import get_blog_post, get_paginated_blog_posts


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
                  {
                      "title": "Post 1",
                      "slug": "post-1",
                      "html_content": "...",
                      "drive_file_id": "...",
                      "categories": ["Python", "Web Development"],
                      "created_at": "2024-01-15 10:30:00"
                  },
                  {
                      "title": "Post 2",
                      "slug": "post-2",
                      "html_content": "...",
                      "drive_file_id": "...",
                      "categories": ["JavaScript", "Frontend"],
                      "created_at": "2024-01-16 14:20:00"
                  }
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


def get_single_post(slug: str) -> tuple[Response, int]:
    """Handles the retrieval of a single blog post by slug and returns a JSON response.

    This function calls the service layer to fetch a blog post by its slug and
    returns it as a JSON response.

    Args:
        slug (str): The unique slug of the blog post.

    Returns:
        tuple[Response, int]: A Flask JSON response containing the blog post details,
        along with the corresponding HTTP status code.

    Example:
        - GET `/blog/post-1`
        - Response:
          ```json
          {
              "title": "Post 1",
              "slug": "post-1",
              "html_content": "Post content...",
              "drive_file_id": "drive_id_1",
              "categories": ["Python", "Web Development", "Flask"],
              "created_at": "2024-01-15 10:30:00"
          }
          ```
    """
    try:
        post = get_blog_post(slug)

        schema = BlogPostSchema()
        serialized_post = schema.dump(post)

        return jsonify(serialized_post), 200

    except BlogPostNotFoundError:
        current_app.logger.info(f"Blog post not found: {slug}")
        return jsonify({"message": "Blog post not found"}), 404

    except RuntimeError as e:
        current_app.logger.error(f"Failed to retrieve blog post: {e}")
        return jsonify({"error": str(e)}), 500  # Internal Server Error