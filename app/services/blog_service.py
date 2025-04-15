"""Service layer for handling blog post business logic.

This module provides functions to fetch paginated blog posts from the database.
"""

import logging

from app.domain.blog_post import BlogPost
from app.exceptions import BlogPostDuplicateError
from app.extensions import db
from app.models.repositories.blog_post_repository import BlogPostRepository

logger = logging.getLogger(__name__)


def get_paginated_blog_posts(page: int, per_page: int) -> tuple[list, int]:
    """Fetches paginated blog posts via the repository.

    This function retrieves blog posts for a given page, ensuring proper pagination
    logic and handling potential errors. It delegates the actual data retrieval
    to the BlogPostRepository.

    Args:
        page (int): The page number to retrieve (must be >= 1).
        per_page (int): The fixed number of posts per page.

    Returns:
        tuple[list, int]: A tuple containing:
            - A list of BlogPost objects (or an empty list if no posts are found).
            - The total number of pages available.

    Raises:
        RuntimeError: If retrieving posts from the repository fails.
    """
    if page < 1:
        logger.warning(f"Invalid page number {page}, defaulting to page 1.")
        page = 1  # Normalize to first page

    session = db.session
    try:
        logger.info(f"Fetching page {page} with {per_page} posts per page.")
        repository = BlogPostRepository(session)
        posts, total_pages = repository.fetch_paginated_blog_posts(page, per_page)

        logger.info(f"Successfully retrieved {len(posts)} blog posts.")
        return posts, total_pages
    except RuntimeError as e:
        logger.error(f"Error in BlogPostService: {e}")
        raise RuntimeError("Failed to retrieve blog posts") from e


def get_all_blog_post_identifiers() -> list[dict]:
    """Get all blog post identifiers via the repository.

    This function delegates to the BlogPostRepository to retrieve a list of blog post
    identifiers from the database. Each identifier includes the slug, title, and
    drive file ID. This is typically used for comparing against external sources
    like Google Drive to determine which posts are unpublished.

    Returns:
        list[dict]: A list of dictionaries containing 'slug', 'title', and 'drive_file_id'.

    Raises:
        RuntimeError: If the repository fails to retrieve the data.
    """
    session = db.session
    try:
        logger.info("Fetching blog post identifiers from the repository.")
        identifiers = BlogPostRepository(session).fetch_all_post_identifiers()

        logger.info(f"Successfully fetched {len(identifiers)} blog post identifiers.")
        return identifiers
    except RuntimeError as e:
        logger.error(f"Error in BlogPostService: {e}")
        raise RuntimeError("Failed to retrieve blog post identifiers") from e


def save_blog_post(validated_data) -> BlogPost:
    """Service function to save a blog post.

    Args:
        validated_data (dict): Dictionary containing validated blog post data.
            Expected fields: title, content, slug, drive_file_id.

    Returns:
        BlogPost: The newly created blog post domain object.

    Raises:
        KeyError: If any required fields are missing.
        BlogPostDuplicateError: If a duplicate blog post is detected.
        RuntimeError: For other unexpected errors during blog post creation.
    """
    required_fields = ['title', 'content', 'slug', 'drive_file_id']

    # Validate required fields
    logger.info("Validating required fields for blog post.")
    for field in required_fields:
        if field not in validated_data:
            logger.error(f"Missing required field: {field}")
            raise KeyError(field)
    logger.info("All required fields are present.")

    session = db.session
    blog_post_repo = BlogPostRepository(session)

    try:
        # Create and save blog post
        logger.info("Saving the blog post to the database.")
        blog_post = blog_post_repo.create_blog_post(
            title=validated_data['title'],
            slug=validated_data['slug'],
            content=validated_data['content'],  # Already sanitized earlier
            drive_file_id=validated_data['drive_file_id']
        )

        logger.info("Blog post saved successfully with title: %s", blog_post.title)
        return blog_post

    except BlogPostDuplicateError as e:
        logger.warning(
            f"Duplicate blog post detected: {e.message} (field: {e.field_name}, "
            f"value: {e.field_value})")
        raise

    except Exception as e:
        logger.error(f"Unexpected error during blog post creation: {str(e)}")
        raise RuntimeError("Failed to save blog post due to an unexpected error.") from e


def get_blog_post(slug: str):
    """Fetches a single blog post by slug via the repository.

    This function retrieves a blog post based on its unique slug. It delegates
    the actual database retrieval to the BlogPostRepository.

    Args:
        slug (str): The slug of the blog post to retrieve.

    Returns:
        BlogPost: The retrieved blog post instance.

    Raises:
        RuntimeError: If retrieving the blog post fails.
    """
    session = db.session
    try:
        logger.info(f"Fetching blog post with slug: {slug}")
        repository = BlogPostRepository(session)
        blog_post = repository.fetch_blog_post_by_slug(slug)

        if not blog_post:
            logger.warning(f"No blog post found for slug: {slug}")
            return None  # Allows the controller to handle a 404 case

        logger.info(f"Successfully retrieved blog post: {blog_post.title}")
        return blog_post

    except RuntimeError as e:
        logger.error(f"Error retrieving blog post: {e}")
        raise RuntimeError("Failed to retrieve blog post") from e
