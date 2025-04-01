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
- fetch_blog_post_by_slug: Retrieves a blog post by its slug.
"""

from typing import List, Optional

from sqlalchemy import select, insert, func, column
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import Session

from app.exceptions import BlogPostDuplicateError, BlogPostNotFoundError
from app.models.tables.blog_post import blog_posts
from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.domain.blog_post import BlogPost
from app.exceptions import BlogPostDuplicateError
from app.models.tables.blog_post import blog_posts


class BlogPostRepository:
    """Repository for handling blog post database operations."""

    def __init__(self, session):
        self.session = session

    def create_blog_post(
            self,
            title: str,
            slug: str,
            content: str,
            drive_file_id: str
    ) -> BlogPost:
        """Create a new blog post using SQLAlchemy.

        Args:
            title (str): The title of the blog post.
            slug (str): The unique slug for the blog post.
            content (str): The content of the blog post.
            drive_file_id (str): The unique Google Drive file ID for the post.

        Returns:
            BlogPost: The newly created BlogPost instance.

        Raises:
            BlogPostDuplicateError: If a blog post with a duplicate slug or
                drive_file_id is detected.
            RuntimeError: If a general database error occurs during the operation.
        """
        try:
            new_post_data = {
                'title': title,
                'slug': slug,
                'content': content,
                'drive_file_id': drive_file_id
            }
            insert_query = insert(blog_posts).values(new_post_data).returning(blog_posts.c.created_at)
            result = self.session.execute(insert_query).scalar_one()
            self.session.commit()

            return BlogPost(
                title=title,
                slug=slug,
                content=content,
                drive_file_id=drive_file_id,
                created_at=result  # Pass database-created timestamp
            )
        except IntegrityError as e:
            self.session.rollback()

            if 'slug' in str(e.orig):
                raise BlogPostDuplicateError(
                    message="A blog post with this slug already exists.",
                    field_name="slug",
                    field_value=slug
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

            return [
                BlogPost(
                    title=row['title'],
                    slug=row['slug'],  # Ensure slug is included
                    content=row['content'],
                    drive_file_id=row['drive_file_id']
                )
                for row in result
            ] if result else []
        except SQLAlchemyError as e:
            raise RuntimeError("Failed to fetch blog posts from the database.") from e

    def fetch_paginated_blog_posts(self, page: int, per_page: int) -> tuple[List[BlogPost], int]:
        """Retrieve paginated blog posts from the database.

        Args:
            page (int): The page number to retrieve.
            per_page (int): The number of posts per page.

        Returns:
            tuple[List[BlogPost], int]: A tuple containing:
                - A list of `BlogPost` objects (or an empty list if no posts are found).
                - The total number of pages.

        Raises:
            RuntimeError: If database retrieval fails.
        """
        try:
            total_posts = self.count_total_blog_posts()
            total_pages = (total_posts + per_page - 1) // per_page  # Ceiling division
            offset = (page - 1) * per_page
            query = select(blog_posts).limit(per_page).offset(offset)
            result = self.session.execute(query).mappings().all()

            posts = [
                BlogPost(
                    title=row['title'],
                    slug=row['slug'],
                    content=row['content'],
                    drive_file_id=row['drive_file_id']
                )
                for row in result
            ] if result else []

            return posts, total_pages
        except SQLAlchemyError as e:
            raise RuntimeError("Failed to fetch paginated blog posts from the database.") from e

    def count_total_blog_posts(self) -> int:
        """Retrieve the total number of blog posts in the database.

        Returns:
            int: The total count of blog posts.

        Raises:
            RuntimeError: If database retrieval fails.
        """
        try:
            query = select(func.count()).select_from(blog_posts)
            total_posts = self.session.execute(query).scalar()
            return total_posts or 0  # Ensure it returns at least 0
        except SQLAlchemyError as e:
            raise RuntimeError("Failed to count blog posts.") from e

    def fetch_blog_post_by_slug(self, slug: str) -> BlogPost:
        """Retrieve a single blog post by its slug.

        Args:
            slug (str): The unique slug of the blog post.

        Returns:
            BlogPost: The retrieved blog post instance.

        Raises:
            BlogPostNotFoundError: If no blog post with the given slug exists.
            RuntimeError: If a database error occurs.
        """
        try:
            query = select(blog_posts).where(column("slug") == slug)
            result = self.session.execute(query).mappings().first()

            if not result:
                raise BlogPostNotFoundError(f"No blog post found with slug {slug}")

            return BlogPost(
                title=result["title"],
                slug=result["slug"],
                content=result["content"],
                drive_file_id=result["drive_file_id"],
                created_at=result["created_at"]  # Pass DB timestamp
            )
        except SQLAlchemyError as e:
            raise RuntimeError("Failed to fetch blog post from the database.") from e

