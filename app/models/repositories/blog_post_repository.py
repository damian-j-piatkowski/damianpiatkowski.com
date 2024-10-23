"""BlogPostRepository for database operations.

This module defines the BlogPostRepository class, responsible for handling
CRUD operations on the blog_posts table. It provides methods for creating and 
fetching blog posts from the database, and raises informative errors in case 
of database issues.

Methods:
- create_blog_post: Inserts a new blog post into the database.
- fetch_all_blog_posts: Retrieves all blog posts from the database.
"""
from typing import List, Dict, Optional

from sqlalchemy import select, insert
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import Session

from app.models.blog_post import blog_posts


class BlogPostRepository:
    """Repository for handling blog post database operations."""

    def __init__(self, session: Session):
        self.session = session

    def create_blog_post(
            self,
            title: str,
            content: str,
            image_small: str,
            image_medium: str,
            image_large: str,
            url: str  # Added URL parameter
    ) -> Optional[Dict[str, str]]:
        """Create a new blog post using SQLAlchemy.

        Args:
            title (str): The title of the blog post.
            content (str): The content of the blog post.
            image_small (str): URL for the small-sized image.
            image_medium (str): URL for the medium-sized image.
            image_large (str): URL for the large-sized image.
            url (str): The unique URL slug for the blog post.

        Returns:
            Optional[Dict[str, str]]: The newly created blog post data, or
                None if an error occurs.
        """
        try:
            new_post = {
                'title': title,
                'content': content,
                'image_small': image_small,
                'image_medium': image_medium,
                'image_large': image_large,
                'url': url
            }
            insert_query = insert(blog_posts).values(new_post)
            self.session.execute(insert_query)
            return new_post
        except IntegrityError:
            self.session.rollback()  # Rollback the transaction on failure
            raise  # Re-raise the IntegrityError
        except SQLAlchemyError as e:
            print(f"Database error occurred while creating a blog post: {e}")
            raise RuntimeError("Failed to create blog post in the database.") from e

    def fetch_all_blog_posts(self) -> List[Dict[str, str]]:
        try:
            # Corrected select statement for SQLAlchemy 1.4+
            query = select(blog_posts)
            result = self.session.execute(
                query).mappings().all()  # Use .mappings() to return dict-like rows
            print(f"Query result: {result}")
            return [dict(row) for row in
                    result] if result else []  # Convert mappings to dict
        except SQLAlchemyError as e:
            print(f"Database error occurred while fetching blog posts: {e}")
            raise RuntimeError(
                "Failed to fetch blog posts from the database.") from e
