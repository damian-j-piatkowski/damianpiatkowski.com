"""Defines the SQLAlchemy table schema for the blog posts.

This module creates a `blog_posts` table using SQLAlchemy's Table API, which represents
the schema for storing blog post records. Each blog post has a unique title and drive file ID,
along with a text content field. The `slug` column stores a URL-friendly identifier for each post.
The `created_at` column is automatically populated with the current timestamp upon record insertion.

Columns:
    - id: Primary key, auto-incremented integer.
    - title: Unique title of the blog post, max length 255 characters.
    - slug: Unique URL-friendly identifier of the blog post, max length 255 characters.
    - content: The main content of the blog post, stored as text.
    - drive_file_id: Unique Google Drive file ID associated with the blog post.
    - created_at: Timestamp of when the post was created, set automatically to the current time.
"""

from sqlalchemy import Table, MetaData, Column, Integer, String, Text, TIMESTAMP, func

metadata = MetaData()

blog_posts = Table(
    'blog_posts', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('title', String(255), nullable=False, unique=True),
    Column('slug', String(255), nullable=False, unique=True),
    Column('content', Text, nullable=False),
    Column('drive_file_id', String(255), nullable=False, unique=True),
    Column('created_at', TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
)
