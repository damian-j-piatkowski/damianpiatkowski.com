"""BlogPostService for handling blog post business logic.

This module defines functions responsible for the business logic layer of blog post operations.
It acts as an intermediary between the controller layer and the BlogPostRepository, coordinating
database access, validation, logging, and error handling.

Methods:
- enrich_with_thumbnails: Attaches resolved thumbnail base paths to blog posts.
- get_all_blog_post_identifiers: Retrieves all blog post identifiers (slug, title, drive_file_id).
- get_all_categories_with_counts: Retrieves all categories with their post counts.
- get_blog_post: Retrieves a blog post by its slug.
- get_blog_posts_by_category: Retrieves blog posts filtered by category.
- get_related_blog_posts: Retrieves related blog posts based on categories and exclude_slug.
- get_paginated_blog_posts: Retrieves paginated blog posts based on page and per-page limits.
- remove_blog_post_by_slug: Deletes a blog post from the database by its slug.
- save_blog_post: Validates and saves a new blog post to the database.
"""

import logging
from typing import List
import os
from flask import current_app, url_for

from app.domain.blog_post import BlogPost
from app.exceptions import BlogPostDuplicateError
from app.extensions import db
from app.models.repositories.blog_post_repository import BlogPostRepository

logger = logging.getLogger(__name__)


def enrich_with_thumbnails(posts: list[dict]) -> list[dict]:
    """Attaches resolved thumbnail base paths to blog posts.

    For each post, this function attaches a `thumb_base` key, which points to the base path
    (without file extension) for thumbnail images like `desktop.jpg`, `mobile.jpg`, etc.

    - If `BLOG_IMAGE_BASE_PATH` in app config is an HTTP URL (e.g., S3 bucket),
      it assumes the images exist remotely and constructs the URL accordingly.

    - If it's a local path (default: "images/blog-thumbnails"), it builds the static URL
      via `url_for()` and checks if the file `desktop.jpg` exists in the expected directory.

    - If `desktop.jpg` is missing, it falls back to `/default/thumbnail` under the same base path.

    Example with local base:
        BLOG_IMAGE_BASE_PATH = "images/blog-thumbnails"

        Input:
            {"slug": "post-1"}
        Result (if file exists):
            {"thumb_base": "/static/images/blog-thumbnails/post-1/thumbnail"}

        Result (if missing):
            {"thumb_base": "/static/images/blog-thumbnails/default/thumbnail"}

    Example with remote base:
        BLOG_IMAGE_BASE_PATH = "https://cdn.example.com/blog-thumbnails"

        Input:
            {"slug": "post-2"}
        Result:
            {"thumb_base": "https://cdn.example.com/blog-thumbnails/post-2/thumbnail"}

    Returns:
        A list of posts with an added `thumb_base` key per post.
    """
    if not posts:
        return []

    blog_image_base = current_app.config.get("BLOG_IMAGE_BASE_PATH", "images/blog-thumbnails")

    for post in posts:
        slug = post.get("slug")
        if not slug:
            continue

        # S3 or remote image base – just build the remote URL
        if blog_image_base.startswith("http"):
            thumb_base = f"{blog_image_base}/{slug}/thumbnail"

        # Local image base – use Flask static path resolution
        else:
            # Default to post-specific thumbnail path
            thumb_base = url_for("static", filename=f"{blog_image_base}/{slug}/thumbnail", _external=False)

            # Check if the desktop image exists on disk
            desktop_path = os.path.join(
                current_app.static_folder, blog_image_base, slug, "thumbnail", "desktop.jpg"
            )

            # Fallback to default thumbnails if missing
            if not os.path.exists(desktop_path):
                thumb_base = url_for("static", filename=f"{blog_image_base}/default/thumbnail", _external=False)

        post["thumb_base"] = thumb_base

    return posts


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

def get_all_categories_with_counts() -> tuple[List[tuple[str, int]], int]:
    """Fetches all categories with their post counts and total unique posts via the repository.

    Returns:
        tuple[List[tuple[str, int]], int]: A tuple containing:
            - List of tuples with (category_name, post_count)
            - Total number of unique blog posts in the database

    Raises:
        RuntimeError: If retrieving categories from the repository fails.
    """
    session = db.session
    try:
        logger.info("Fetching all categories with counts and total posts")
        repository = BlogPostRepository(session)

        # Get categories with their counts
        categories_with_counts = repository.fetch_all_categories_with_counts()

        # Get total unique posts count
        total_posts = repository.count_total_blog_posts()

        logger.info(f"Successfully retrieved {len(categories_with_counts)} categories and {total_posts} total posts")
        return categories_with_counts, total_posts
    except RuntimeError as e:
        logger.error(f"Error in BlogPostService getting categories: {e}")
        raise RuntimeError("Failed to retrieve categories with counts") from e


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


def get_blog_posts_by_category(page: int, per_page: int, category: str) -> tuple[list, int]:
    """Fetches paginated blog posts filtered by category via the repository.

    Args:
        page (int): The page number to retrieve (must be >= 1).
        per_page (int): The fixed number of posts per page.
        category (str): The category to filter by.

    Returns:
        tuple[list, int]: A tuple containing the filtered posts and total pages.

    Raises:
        RuntimeError: If retrieving posts from the repository fails.
    """
    if page < 1:
        logger.warning(f"Invalid page number {page}, defaulting to page 1.")
        page = 1

    session = db.session
    try:
        logger.info(f"Fetching page {page} with {per_page} posts per page for category: {category}")
        repository = BlogPostRepository(session)
        posts, total_pages = repository.fetch_posts_by_category(category, page, per_page)

        logger.info(f"Successfully retrieved {len(posts)} blog posts for category: {category}")
        return posts, total_pages
    except RuntimeError as e:
        logger.error(f"Error in BlogPostService: {e}")
        raise RuntimeError("Failed to retrieve blog posts by category") from e


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


def get_related_blog_posts(categories: List[str], exclude_slug: str, limit: int = 3) -> List[BlogPost]:
    """Fetches related blog posts that share categories with the current post.

    Args:
        categories (List[str]): Categories of the current post.
        exclude_slug (str): Slug of the current post to exclude.
        limit (int): Maximum number of related posts to return.

    Returns:
        List[BlogPost]: List of related blog posts.

    Raises:
        RuntimeError: If retrieving related posts fails.
    """
    session = db.session
    try:
        logger.info(f"Fetching related posts for categories: {categories}, excluding: {exclude_slug}")
        repository = BlogPostRepository(session)
        related_posts = repository.fetch_related_posts(categories, exclude_slug, limit)

        logger.info(f"Successfully retrieved {len(related_posts)} related blog posts")
        return related_posts
    except RuntimeError as e:
        logger.error(f"Error fetching related posts: {e}")
        raise RuntimeError("Failed to retrieve related blog posts") from e


def remove_blog_post_by_slug(slug: str) -> None:
    """Removes a blog post from the database by slug.

    This function delegates to the BlogPostRepository to delete a blog post by
    its unique slug. It logs the result of the operation.

    Args:
        slug (str): The slug of the blog post to delete.

    Raises:
        RuntimeError: If the repository fails to delete the blog post.
    """
    session = db.session
    try:
        logger.info(f"Attempting to remove blog post with slug: {slug}")
        BlogPostRepository(session).delete_blog_post_by_slug(slug)
        logger.info(f"Successfully removed blog post with slug: {slug}")
    except RuntimeError as e:
        logger.error(f"Failed to remove blog post: {e}")
        raise RuntimeError("Failed to delete blog post") from e


def save_blog_post(validated_data) -> BlogPost:
    """Service function to save a blog post.

    Args:
        validated_data (dict): Dictionary containing validated blog post data.
            Expected fields: title, html_content, slug, drive_file_id, categories (optional).

    Returns:
        BlogPost: The newly created blog post domain object.

    Raises:
        KeyError: If any required fields are missing.
        BlogPostDuplicateError: If a duplicate blog post is detected.
        RuntimeError: For other unexpected errors during blog post creation.
    """
    required_fields = ['title', 'html_content', 'slug', 'drive_file_id']

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
        # Extract categories (optional field)
        categories = validated_data.get('categories', [])

        # Create and save blog post
        logger.info("Saving the blog post to the database.")
        blog_post = blog_post_repo.create_blog_post(
            title=validated_data['title'],
            slug=validated_data['slug'],
            html_content=validated_data['html_content'],  # Already sanitized earlier
            drive_file_id=validated_data['drive_file_id'],
            categories=categories
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
