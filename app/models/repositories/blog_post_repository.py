"""BlogPostRepository for database operations.

This module defines the BlogPostRepository class, responsible for handling
CRUD operations on the blog_posts table. It provides methods for creating and
fetching blog posts from the database, and raises informative errors in case
of database issues. The blog posts are stored with HTML content that has been
converted from markdown during the import process. Categories are stored as JSON arrays.

Methods:
- count_total_blog_posts: Returns the total number of blog posts in the database.
- create_blog_post: Inserts a new blog post with HTML content and categories into the database and returns the BlogPost instance.
- delete_blog_post_by_slug: Deletes a blog post from the database by its slug.
- fetch_all_categories_with_counts: Retrieves all categories with their post counts.
- fetch_all_post_identifiers: Retrieves minimal metadata (slug, title, drive_file_id) for all blog posts.
- fetch_blog_post_by_slug: Retrieves a blog post by its slug.
- fetch_paginated_blog_posts: Retrieves paginated blog posts from the database based on page and limit parameters.
- fetch_posts_by_category: Retrieves paginated blog posts filtered by category.
- fetch_related_posts: Retrieves posts that share categories with the current post, excluding the current post.
"""

import json
from typing import List, Optional

from sqlalchemy import delete, insert, select, func, column, or_
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

    @staticmethod
    def _hydrate_blog_post(row: dict) -> BlogPost:
        """Constructs a BlogPost domain object from a raw database row mapping.

        Args:
            row (dict): A dictionary representing a row from the database.

        Returns:
            BlogPost: The hydrated domain model.
        """
        return BlogPost(
            title=row["title"],
            slug=row["slug"],
            html_content=row["html_content"],
            drive_file_id=row["drive_file_id"],
            categories=row.get("categories") or [],
            read_time_minutes=row["read_time_minutes"],
            meta_description=row["meta_description"],
            keywords=row.get("keywords") or [],
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        )

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
            drive_file_id: str,
            categories: List[str] = None,
            read_time_minutes: int = 1,
            meta_description: str = "",
            keywords: List[str] = None
    ) -> BlogPost:
        """Creates a new blog post using SQLAlchemy."""
        try:
            new_post_data = {
                'title': title,
                'slug': slug,
                'html_content': html_content,
                'drive_file_id': drive_file_id,
                'categories': categories or [],
                'read_time_minutes': read_time_minutes,
                'meta_description': meta_description,
                'keywords': keywords or []
            }

            insert_query = insert(blog_posts).values(new_post_data)
            self.session.execute(insert_query)
            self.session.commit()

            fetch_query = select(blog_posts).where(blog_posts.c.slug == slug)
            result = self.session.execute(fetch_query).mappings().one()

            return self._hydrate_blog_post(dict(result))

        except IntegrityError as e:
            self.session.rollback()
            if 'slug' in str(e.orig):
                raise BlogPostDuplicateError("A blog post with this slug already exists.", "slug", slug)
            elif 'drive_file_id' in str(e.orig):
                raise BlogPostDuplicateError("A blog post with this drive_file_id already exists.", "drive_file_id",
                                             drive_file_id)
            elif 'title' in str(e.orig):
                raise BlogPostDuplicateError("A blog post with this title already exists.", "title", title)
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

    def fetch_all_categories_with_counts(self) -> List[tuple[str, int]]:
        """Retrieves all categories with their post counts.

        Returns:
            List[tuple[str, int]]: A list of tuples containing (category_name, post_count)
            sorted by count in descending order.

        Raises:
            RuntimeError: If database retrieval fails.
        """
        try:
            from collections import Counter

            # Fetch all posts with their categories using pure SQLAlchemy
            query = select(blog_posts.c.categories).where(
                blog_posts.c.categories.isnot(None)
            )

            result = self.session.execute(query).fetchall()

            # Process categories in Python (more reliable than complex JSON SQL)
            all_categories = []
            for row in result:
                categories = row[0] if row[0] else []
                all_categories.extend(categories)

            # Count occurrences and sort by count (descending)
            category_counts = Counter(all_categories)
            categories_with_counts = category_counts.most_common()

            return categories_with_counts

        except SQLAlchemyError as e:
            raise RuntimeError("Failed to fetch categories with counts from the database.") from e

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

            return self._hydrate_blog_post(dict(result))
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

            posts = [self._hydrate_blog_post(dict(row)) for row in result] if result else []

            return posts, total_pages
        except SQLAlchemyError as e:
            raise RuntimeError("Failed to fetch paginated blog posts from the database.") from e

    def fetch_posts_by_category(self, category: str, page: int, per_page: int) -> tuple[List[BlogPost], int]:
        """Retrieves paginated blog posts filtered by category.

        Args:
            category (str): The category to filter by.
            page (int): The page number to retrieve (1-based indexing).
            per_page (int): The number of blog posts to retrieve per page.

        Returns:
            tuple[List[BlogPost], int]: A tuple containing the filtered posts and total pages.

        Raises:
            RuntimeError: If database retrieval fails.
        """
        try:
            # Count total posts in this category
            count_query = select(func.count()).select_from(blog_posts).where(
                func.json_contains(blog_posts.c.categories, json.dumps([category]))
            )
            total_posts = self.session.execute(count_query).scalar() or 0
            total_pages = (total_posts + per_page - 1) // per_page

            # Get paginated posts for this category
            offset = (page - 1) * per_page
            query = select(blog_posts).where(
                func.json_contains(blog_posts.c.categories, json.dumps([category]))
            ).order_by(blog_posts.c.created_at.desc()).limit(per_page).offset(offset)

            result = self.session.execute(query).mappings().all()

            posts = [self._hydrate_blog_post(dict(row)) for row in result] if result else []

            return posts, total_pages

        except SQLAlchemyError as e:
            raise RuntimeError("Failed to fetch posts by category from the database.") from e

    def fetch_related_posts(self, categories: List[str], exclude_slug: str, limit: int = 3) -> List[BlogPost]:
        """Get posts that share categories with the current post, excluding the current post.

        Args:
            categories (List[str]): List of categories to find related posts for.
            exclude_slug (str): Slug of the current post to exclude from results.
            limit (int): Maximum number of related posts to return.

        Returns:
            List[BlogPost]: List of related blog posts.

        Raises:
            RuntimeError: If database retrieval fails.
        """
        try:
            if not categories:
                return []

            # Build conditions for each category - posts that contain ANY of these categories
            category_conditions = [
                func.json_contains(blog_posts.c.categories, json.dumps([cat]))
                for cat in categories
            ]

            query = select(blog_posts).where(
                blog_posts.c.slug != exclude_slug,
                or_(*category_conditions)
            ).order_by(blog_posts.c.created_at.desc()).limit(limit)

            result = self.session.execute(query).mappings().all()

            return [self._hydrate_blog_post(dict(row)) for row in result] if result else []

        except SQLAlchemyError as e:
            raise RuntimeError("Failed to fetch related posts from the database.") from e
