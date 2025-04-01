"""Defines the BlogPost domain model with essential attributes for a blog post.

This module defines the BlogPost domain model, representing the core attributes
of a blog post within the application.

The BlogPost class encapsulates essential properties of a blog post, including
the title, content, a unique slug for URL generation, an associated Google Drive file ID,
and a creation timestamp sourced directly from the database.

This model is designed to be ORM-agnostic, making it versatile for use with
different data storage layers.

Classes:
    BlogPost: Represents a blog post with a title, content, unique slug, Google Drive file ID,
              and a database-assigned creation timestamp.
"""

from datetime import datetime


class BlogPost:
    """Represents a blog post in the domain model."""

    def __init__(self, title: str, content: str, slug: str, drive_file_id: str, created_at: datetime) -> None:
        """
        Initializes a new BlogPost instance with title, content, slug, drive file ID, and creation timestamp.

        Args:
            title (str): The title of the blog post.
            content (str): The content of the blog post.
            slug (str): A unique, URL-friendly identifier for the blog post.
            drive_file_id (str): The unique file ID from Google Drive.
            created_at (datetime): The timestamp when the post was created, sourced from the database.
        """
        self.title = title
        self.content = content
        self.slug = slug
        self.drive_file_id = drive_file_id
        self.created_at = created_at  # Sourced from the database
