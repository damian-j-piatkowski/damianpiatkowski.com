"""Defines the BlogPost domain model with essential attributes for a blog post.

This module defines the BlogPost domain model, representing the core attributes
of a blog post within the application.

The BlogPost class encapsulates essential properties of a blog post, including
the title, HTML content (converted from markdown during import), a unique slug for URL generation,
an associated Google Drive file ID, categories for organization, and a creation timestamp
sourced directly from the database.

This model is designed to be ORM-agnostic, making it versatile for use with
different data storage layers.

Classes:
    BlogPost: Represents a blog post with a title, HTML content, unique slug, Google Drive file ID,
              categories, and a database-assigned creation timestamp.
"""

from datetime import datetime
from typing import List, Optional


class BlogPost:
    """Represents a blog post in the domain model."""

    def __init__(self, title: str, html_content: str, slug: str, drive_file_id: str,
                 created_at: datetime, categories: Optional[List[str]] = None) -> None:
        """Initializes a new BlogPost instance with title, HTML content, slug, drive file ID, creation timestamp, and categories.

        Args:
            title (str): The title of the blog post.
            html_content (str): The HTML content of the blog post.
            slug (str): A unique, URL-friendly identifier for the blog post.
            drive_file_id (str): The unique file ID from Google Drive.
            created_at (datetime): The timestamp when the post was created, sourced from the database.
            categories (Optional[List[str]]): List of category strings for organizing the post. Defaults to empty list.
        """
        self.title = title
        self.html_content = html_content
        self.slug = slug
        self.drive_file_id = drive_file_id
        self.created_at = created_at  # Sourced from the database
        self.categories = categories or []  # Default to empty list if None