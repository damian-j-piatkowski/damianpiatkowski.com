"""BlogPostRepository for database operations.

This module defines the BlogPostRepository class, responsible for handling
CRUD operations on the blog_posts table. It provides methods for creating and
fetching blog posts from the database, and raises informative errors in case
of database issues. The blog posts are stored with HTML content that has been
converted from markdown during the import process.

Methods:
- count_total_blog_posts: Returns the total number of blog posts in the database.
- create_blog_post: Inserts a new blog post with HTML content into the database and returns the BlogPost instance.
- delete_blog_post_by_slug: Deletes a blog post from the database by its slug.
- fetch_all_post_identifiers: Retrieves minimal metadata (slug, title, drive_file_id) for all blog posts.
- fetch_blog_post_by_slug: Retrieves a blog post by its slug.
- fetch_paginated_blog_posts: Retrieves paginated blog posts from the database based on page and limit parameters.
"""

from typing import List

from sqlalchemy import delete, insert, select
from sqlalchemy import func, column
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.domain.blog_post import BlogPost
from app.exceptions import BlogPostDuplicateError
from app.exceptions import BlogPostNotFoundError
from app.models.tables.blog_post import blog_posts


class BlogPostRepository:
    """Repository for handling blog post database operations."""

    def __init__(self, session: Session) -> None:
        """Initializes the repository with a database session.

        Args:
            session (Session): SQLAlchemy database session for database operations.
        """
        self.session = session

    def count_total_blog_posts(self) -> int:
        """Retrieves the total number of blog posts in the database.

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

    def create_blog_post(
            self,
            title: str,
            slug: str,
            html_content: str,
            drive_file_id: str
    ) -> BlogPost:
        """Creates a new blog post using SQLAlchemy.

        Args:
            title (str): The title of the blog post.
            slug (str): The unique slug for the blog post.
            html_content (str): The HTML content of the blog post.
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
                'html_content': html_content,
                'drive_file_id': drive_file_id
            }

            # First, do the insert
            insert_query = insert(blog_posts).values(new_post_data)
            self.session.execute(insert_query)
            self.session.commit()

            # Then fetch the newly created post using its slug
            fetch_query = select(blog_posts).where(blog_posts.c.slug == slug)
            result = self.session.execute(fetch_query).mappings().one()

            return BlogPost(
                title=title,
                slug=slug,
                html_content=html_content,
                drive_file_id=drive_file_id,
                created_at=result['created_at']
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
            elif 'title' in str(e.orig):
                raise BlogPostDuplicateError(
                    message="A blog post with this title already exists.",
                    field_name="title",
                    field_value=title
                )
            raise

        except SQLAlchemyError as e:
            self.session.rollback()
            raise RuntimeError("Failed to create blog post in the database.") from e

    def delete_blog_post_by_slug(self, slug: str) -> None:
        """Deletes a blog post from the database by its slug.

        Args:
            slug (str): The unique slug of the blog post to delete.

        Raises:
            BlogPostNotFoundError: If no blog post with the given slug exists.
            RuntimeError: If a database error occurs.
        """
        try:
            delete_query = delete(blog_posts).where(column("slug") == slug)
            result = self.session.execute(delete_query)

            if result.rowcount == 0:
                self.session.rollback()
                raise BlogPostNotFoundError(f"No blog post found with slug {slug}")

            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RuntimeError("Failed to delete blog post from the database.") from e

    def fetch_all_post_identifiers(self) -> List[dict]:
        """Fetches slugs and other identifiers of all blog posts from the database.

        Returns:
            List[dict]: A list of dicts with 'slug', 'title', and 'drive_file_id'.
        """
        try:
            query = select(
                blog_posts.c.slug,
                blog_posts.c.title,
                blog_posts.c.drive_file_id
            )
            result = self.session.execute(query).mappings().all()

            return [
                {
                    "slug": row["slug"],
                    "title": row["title"],
                    "drive_file_id": row["drive_file_id"]
                }
                for row in result
            ] if result else []

        except SQLAlchemyError as e:
            raise RuntimeError("Failed to fetch blog post identifiers from the database.") from e

    def fetch_blog_post_by_slug(self, slug: str) -> BlogPost:
        """Retrieves a single blog post by its slug.

        Args:
            slug (str): The unique slug of the blog post to retrieve.

        Returns:
            BlogPost: The retrieved blog post instance.

        Raises:
            BlogPostNotFoundError: If no blog post with the given slug exists.
            RuntimeError: If a database error occurs during retrieval.
        """
        try:
            query = select(blog_posts).where(column("slug") == slug)
            result = self.session.execute(query).mappings().first()

            if not result:
                raise BlogPostNotFoundError(f"No blog post found with slug {slug}")

            return BlogPost(
                title=result["title"],
                slug=result["slug"],
                html_content=result["html_content"],
                drive_file_id=result["drive_file_id"],
                created_at=result["created_at"]
            )
        except SQLAlchemyError as e:
            raise RuntimeError("Failed to fetch blog post from the database.") from e

    def fetch_paginated_blog_posts(self, page: int, per_page: int) -> tuple[List[BlogPost], int]:
        """Retrieves a paginated list of blog posts from the database.

        Args:
            page (int): The page number to retrieve (1-based indexing).
            per_page (int): The number of blog posts to retrieve per page.

        Returns:
            tuple[List[BlogPost], int]: A tuple containing:
                - List[BlogPost]: The list of blog posts for the requested page.
                - int: The total number of pages available.

        Raises:
            RuntimeError: If database retrieval fails.

        Notes:
            - Returns an empty list if the page is out of range.
            - Total pages is calculated as ceiling(total_posts / per_page).
            - Blog posts are ordered by their natural database order.
        """
        try:
            total_posts = self.count_total_blog_posts()
            total_pages = (total_posts + per_page - 1) // per_page
            offset = (page - 1) * per_page
            query = select(blog_posts).limit(per_page).offset(offset)
            result = self.session.execute(query).mappings().all()

            posts = [
                BlogPost(
                    title=row['title'],
                    slug=row['slug'],
                    html_content=row['html_content'],
                    drive_file_id=row['drive_file_id'],
                    created_at=row['created_at']
                )
                for row in result
            ] if result else []

            return posts, total_pages
        except SQLAlchemyError as e:
            raise RuntimeError("Failed to fetch paginated blog posts from the database.") from e
