from app.extensions import db
from app.models.repositories.blog_post_repository import BlogPostRepository


def fetch_all_blog_posts():
    """Service function to fetch all blog posts."""
    session = db.session
    try:
        posts = BlogPostRepository(session).fetch_all_blog_posts()
        return posts
    except RuntimeError as e:
        # Log the error (you might want to use a proper logging system)
        print(f"Error in BlogPostService: {e}")
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

    for field in required_fields:
        if field not in validated_data:
            raise KeyError(field)

    session = db.session
    blog_post_repo = BlogPostRepository(session)

    blog_post = blog_post_repo.create_blog_post(
        title=validated_data['title'],
        content=validated_data['content'],
        image_small=validated_data['image_small'],
        image_medium=validated_data['image_medium'],
        image_large=validated_data['image_large'],
        url=validated_data['url']
    )

    return blog_post
