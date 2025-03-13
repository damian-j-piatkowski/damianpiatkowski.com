"""
Service layer for handling blog post business logic.

This module provides functions to fetch paginated blog posts from the database.
"""

import logging

from app.exceptions import BlogPostDuplicateError
from app.extensions import db
from app.models.repositories.blog_post_repository import BlogPostRepository
from app.services.sanitization_service import sanitize_html

logger = logging.getLogger(__name__)


def get_paginated_blog_posts(page: int, per_page: int) -> tuple[list, int]:
    """Retrieve paginated blog posts from the database.

    Args:
        page (int): The page number to retrieve.
        per_page (int): The number of posts per page.

    Returns:
        tuple[list, int]: A tuple containing:
            - A list of BlogPost objects (or an empty list if no posts are found).
            - The total number of pages.

    Raises:
        RuntimeError: If database retrieval fails.
    """
    session = db.session
    try:
        logger.info(f"Fetching page {page} with {per_page} posts per page.")
        repository = BlogPostRepository(session)
        posts, total_pages = repository.get_paginated_blog_posts(page, per_page)

        logger.info(f"Successfully retrieved {len(posts)} blog posts.")
        return posts, total_pages
    except RuntimeError as e:
        logger.error(f"Error in BlogPostService: {e}")
        raise RuntimeError("Failed to retrieve blog posts") from e


def fetch_all_blog_posts():
    """Service function to fetch all blog posts."""
    session = db.session
    try:
        logger.info("Fetching all blog posts from the database.")
        posts = BlogPostRepository(session).fetch_all_blog_posts()
        logger.info("Successfully fetched blog posts.")
        return posts  # List[BlogPost]
    except RuntimeError as e:
        logger.error(f"Error in BlogPostService: {e}")
        raise RuntimeError("Failed to retrieve blog posts") from e


def save_blog_post(validated_data):
    """Service function to save a blog post.

    Args:
        validated_data (dict): Dictionary containing validated blog post data.
            Expected fields: title, content, image_small, image_medium, image_large, url.

    Returns:
        dict: A dictionary containing the newly created blog post's data.

    Raises:
        KeyError: If any required fields are missing.
        BlogPostDuplicateError: If a duplicate blog post is detected.
        RuntimeError: For other unexpected errors during blog post creation.
    """
    required_fields = ['title', 'content', 'drive_file_id']

    # Check for required fields
    logger.info("Validating required fields for blog post.")
    for field in required_fields:
        if field not in validated_data:
            logger.error(f"Missing required field: {field}")
            raise KeyError(field)
    logger.info("All required fields are present.")

    # Sanitize HTML content before saving
    logger.info("Sanitizing HTML content for the blog post.")
    validated_data['content'] = sanitize_html(validated_data['content'])
    logger.info("HTML content sanitized successfully.")

    session = db.session
    blog_post_repo = BlogPostRepository(session)

    try:
        # Create and save blog post
        logger.info("Saving the blog post to the database.")
        blog_post = blog_post_repo.create_blog_post(
            title=validated_data['title'],
            content=validated_data['content'],
            drive_file_id=validated_data.get('drive_file_id', '')
        )

        logger.info("Blog post saved successfully with title: %s", blog_post.title)

        # Return a dictionary representation of the BlogPost instance
        return {
            'title': blog_post.title,
            'content': blog_post.content,
            'drive_file_id': blog_post.drive_file_id,
            'created_at': blog_post.created_at
        }

    except BlogPostDuplicateError as e:
        # Log the duplicate error and re-raise
        logger.warning(
            f"Duplicate blog post detected: {e.message} (field: {e.field_name}, "
            f"value: {e.field_value})")
        raise

    except Exception as e:
        # Log unexpected errors and re-raise
        logger.error(f"Unexpected error during blog post creation: {str(e)}")
        raise RuntimeError("Failed to save blog post due to an unexpected error.") from e
