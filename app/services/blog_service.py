from app.models.repositories.blog_post_repository import BlogPostRepository
from app.extensions import db


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
    """Service function to save a blog post."""
    session = db.session
    blog_post_repo = BlogPostRepository(session)
    try:
        blog_post = blog_post_repo.create_blog_post(
            title=validated_data['title'],
            content=validated_data['content'],
            image_small=validated_data['image_small'],
            image_medium=validated_data['image_medium'],
            image_large=validated_data['image_large']
        )
        session.commit()
        return blog_post
    except RuntimeError as e:
        # Log the error or take action
        print(f"Error in service while saving blog post: {e}")
        session.rollback()  # Rollback the transaction on failure
        raise

# todo finish