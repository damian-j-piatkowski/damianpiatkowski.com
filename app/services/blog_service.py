import logging

from app.extensions import db
from app.models.repositories.blog_post_repository import BlogPostRepository
from app.services.sanitization_service import sanitize_html

logger = logging.getLogger(__name__)


def fetch_all_blog_posts():
    """Service function to fetch all blog posts."""
    session = db.session
    try:
        logger.info("Fetching all blog posts from the database.")
        posts = BlogPostRepository(session).fetch_all_blog_posts()
        logger.info("Successfully fetched blog posts.")
        return posts
    except RuntimeError as e:
        logger.error(f"Error in BlogPostService: {e}")
        raise RuntimeError("Failed to retrieve blog posts") from e


def save_blog_post(validated_data):
    """Service function to save a blog post.

    Args:
        validated_data (dict): Dictionary containing validated blog post data.
            Expected fields: title, content, image_small, image_medium, image_large, url.

    Returns:
        dict: The newly created blog post data.

    Raises:
        KeyError: If any required fields are missing.
    """
    required_fields = ['title', 'content', 'image_small', 'image_medium', 'image_large', 'url']

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

    # Create and save blog post
    logger.info("Saving the blog post to the database.")
    blog_post = blog_post_repo.create_blog_post(
        title=validated_data['title'],
        content=validated_data['content'],
        image_small=validated_data['image_small'],
        image_medium=validated_data['image_medium'],
        image_large=validated_data['image_large'],
        url=validated_data['url']
    )
    logger.info("Blog post saved successfully with ID: %s", blog_post.get('id', 'unknown'))

    return blog_post
