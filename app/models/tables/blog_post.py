"""Defines the SQLAlchemy table schema for the blog posts.

This module creates a `blog_posts` table using SQLAlchemy's Table API, which represents
the schema for storing blog post records. Each blog post has a unique title and drive file ID,
along with an HTML content field. The `slug` column stores a URL-friendly identifier for each post.
The `created_at` column is automatically populated with the current timestamp upon record insertion.
The `categories` column stores a JSON array of category strings for organizing posts.

Columns:
    - id: Primary key, auto-incremented integer.
    - title: Unique title of the blog post, max length 255 characters.
    - slug: Unique URL-friendly identifier of the blog post, max length 255 characters.
    - html_content: The main content of the blog post in HTML format, stored as text.
    - drive_file_id: Unique Google Drive file ID associated with the blog post.
    - categories: JSON array of category strings for post organization.
    - created_at: Timestamp of when the post was created, set automatically to the current time.
"""

from sqlalchemy import Table, MetaData, Column, Integer, String, Text, TIMESTAMP, JSON, func

metadata = MetaData()

blog_posts = Table(
    'blog_posts', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('title', String(255), nullable=False, unique=True),
    Column('slug', String(255), nullable=False, unique=True),
    Column('html_content', Text, nullable=False),  # Changed from 'content' to 'html_content'
    Column('drive_file_id', String(255), nullable=False, unique=True),
    Column('categories', JSON, nullable=True, default=[]),  # New categories column
    Column('created_at', TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
)