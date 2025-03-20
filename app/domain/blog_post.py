"""Defines the BlogPost domain model with essential attributes for a blog post.

This module defines the BlogPost domain model, representing the core attributes
of a blog post within the application.

The BlogPost class encapsulates essential properties of a blog post, including
the title, content, a unique slug for URL generation, an associated Google Drive file ID,
and an automatically assigned timestamp for when the post was created.

This model is designed to be ORM-agnostic, making it versatile for use with
different data storage layers. The `created_at` timestamp is set automatically
upon instantiation to record the post creation time.

Classes:
    BlogPost: Represents a blog post with a title, content, unique slug, Google Drive file ID,
              and creation timestamp.
"""

from datetime import datetime, timezone


class BlogPost:
    """Represents a blog post in the domain model."""

    def __init__(self, title: str, content: str, slug: str, drive_file_id: str) -> None:
        """
        Initializes a new BlogPost instance with title, content, slug, and drive file ID.
        Automatically sets the creation timestamp to the current time.

        Args:
            title (str): The title of the blog post.
            content (str): The content of the blog post.
            slug (str): A unique, URL-friendly identifier for the blog post.
            drive_file_id (str): The unique file ID from Google Drive.
        """
        self.title = title
        self.content = content
        self.slug = slug
        self.drive_file_id = drive_file_id
        self.created_at = datetime.now(timezone.utc)  # Use UTC timestamp
