"""BlogPostRepository for database operations.

This module defines the BlogPostRepository class, responsible for handling
CRUD operations on the blog_posts table. It provides methods for creating and
fetching blog posts from the database, and raises informative errors in case
of database issues.

Methods:
- create_blog_post: Inserts a new blog post into the database and returns the BlogPost instance.
- fetch_all_blog_posts: Retrieves all blog posts as BlogPost instances from the database.
- fetch_paginated_blog_posts: Retrieves paginated blog posts from the database based on page and limit parameters.
- count_total_blog_posts: Returns the total number of blog posts in the database.
"""

from typing import List, Optional

from sqlalchemy import select, insert, func
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import Session

from app.domain.blog_post import BlogPost
from app.exceptions import BlogPostDuplicateError
from app.models.tables.blog_post import blog_posts


class BlogPostRepository:
    """Repository for handling blog post database operations."""

    def __init__(self, session: Session):
        self.session = session

    def create_blog_post(
            self,
            title: str,
            content: str,
            drive_file_id: str
    ) -> Optional[BlogPost]:
        """Create a new blog post using SQLAlchemy.

        Args:
            title (str): The title of the blog post.
            content (str): The content of the blog post.
            drive_file_id (str): The unique Google Drive file ID for the post.

        Returns:
            Optional[BlogPost]: The newly created BlogPost instance, or
                None if an error occurs.

        Raises:
            BlogPostDuplicateError: If a blog post with a duplicate title or
                drive_file_id is detected.
            RuntimeError: If a general database error occurs during the operation.
        """
        try:
            new_post_data = {
                'title': title,
                'content': content,
                'drive_file_id': drive_file_id
            }
            insert_query = insert(blog_posts).values(new_post_data)
            self.session.execute(insert_query)
            self.session.commit()  # Commit the transaction

            # Return a new BlogPost instance
            return BlogPost(
                title=title,
                content=content,
                drive_file_id=drive_file_id
            )
        except IntegrityError as e:
            self.session.rollback()

            # Detect which unique constraint failed
            if 'title' in str(e.orig):
                raise BlogPostDuplicateError(
                    message="A blog post with this title already exists.",
                    field_name="title",
                    field_value=title
                )
            elif 'drive_file_id' in str(e.orig):
                raise BlogPostDuplicateError(
                    message="A blog post with this drive_file_id already exists.",
                    field_name="drive_file_id",
                    field_value=drive_file_id
                )
            raise
        except SQLAlchemyError as e:
            raise RuntimeError("Failed to create blog post in the database.") from e

    def fetch_all_blog_posts(self) -> List[BlogPost]:
        """Fetch all blog posts from the database.

        Returns:
            List[BlogPost]: A list of BlogPost instances.

        Raises:
            RuntimeError: If a database error occurs.
        """
        try:
            query = select(blog_posts)
            result = self.session.execute(query).mappings().all()

            # Convert database rows to BlogPost instances
            return [
                BlogPost(
                    title=row['title'],
                    content=row['content'],
                    drive_file_id=row['drive_file_id']
                )
                for row in result
            ] if result else []
        except SQLAlchemyError as e:
            raise RuntimeError("Failed to fetch blog posts from the database.") from e

    def fetch_paginated_blog_posts(self, page: int, limit: int) -> tuple[List[BlogPost], int]:
        """Fetch paginated blog posts and return total pages count."""
        try:
            total_posts = self.count_total_blog_posts()
            total_pages = (total_posts + limit - 1) // limit  # Ceiling division
            offset = (page - 1) * limit
            query = select(blog_posts).limit(limit).offset(offset)
            result = self.session.execute(query).mappings().all()

            posts = [
                BlogPost(
                    title=row['title'],
                    content=row['content'],
                    drive_file_id=row['drive_file_id']
                )
                for row in result
            ] if result else []

            return posts, total_pages
        except SQLAlchemyError as e:
            raise RuntimeError("Failed to fetch paginated blog posts from the database.") from e

    def count_total_blog_posts(self) -> int:
        """Returns the total number of blog posts in the database.

        Returns:
            int: The total count of blog posts.

        Raises:
            RuntimeError: If a database error occurs.
        """
        try:
            query = select(func.count()).select_from(blog_posts)
            total_posts = self.session.execute(query).scalar()
            return total_posts or 0  # Ensure it returns at least 0
        except SQLAlchemyError as e:
            raise RuntimeError("Failed to count blog posts.") from e
