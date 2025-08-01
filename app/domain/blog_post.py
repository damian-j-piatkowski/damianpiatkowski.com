"""Defines the BlogPost domain model with essential attributes for a blog post.

This module defines the BlogPost domain model, representing the core attributes
of a blog post within the application.

The BlogPost class encapsulates essential properties of a blog post, including:
- Title and HTML content (converted from markdown during import)
- A unique slug for URL generation
- A Google Drive file ID identifying the source document
- Estimated reading time in minutes
- SEO metadata including meta description and keywords
- A list of categories for content organization
- Timestamps for creation and last update

All date/time fields and read-time values are expected to be sourced
directly from the database. This model is designed to be ORM-agnostic,
making it versatile for use across different data storage layers.

Classes:
    BlogPost: Represents a blog post with all relevant attributes including content,
              metadata, categories, and timestamps.
"""

from datetime import datetime
from typing import List, Optional



class BlogPost:
    """Represents a blog post in the domain model.

    This class captures all relevant information for a blog post, including metadata
    for SEO and estimated read time. It serves as a clean domain representation used
    throughout the application, distinct from raw database rows.
    """

    def __init__(
            self,
            title: str,
            html_content: str,
            slug: str,
            drive_file_id: str,
            created_at: datetime,
            updated_at: Optional[datetime],
            read_time_minutes: int,
            meta_description: str,
            keywords: Optional[List[str]],
            categories: Optional[List[str]] = None
    ) -> None:
        """Initializes a new BlogPost instance with all relevant attributes.

        Args:
            title (str): The title of the blog post.
            html_content (str): The HTML content of the blog post.
            slug (str): A unique, URL-friendly identifier for the blog post.
            drive_file_id (str): The unique file ID from Google Drive.
            created_at (datetime): Timestamp when the post was created.
            updated_at (Optional[datetime]): Timestamp of the last update.
            read_time_minutes (int): Estimated time in minutes to read the blog post.
            meta_description (str): A short description of the post for SEO.
            keywords (Optional[List[str]]): A list of keyword strings for SEO metadata.
            categories (Optional[List[str]]): List of categories. Defaults to an empty list.
        """
        self.title = title
        self.html_content = html_content
        self.slug = slug
        self.drive_file_id = drive_file_id
        self.created_at = created_at  # Sourced from the database
        self.updated_at = updated_at  # Sourced from the database
        self.read_time_minutes = read_time_minutes  # Sourced from the database
        self.meta_description = meta_description
        self.keywords = keywords or []
        self.categories = categories or []
