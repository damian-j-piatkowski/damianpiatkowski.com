"""Defines the SQLAlchemy table schema for the blog posts.

This module creates a `blog_posts` table using SQLAlchemy's Table API, which represents
the schema for storing blog post records. Each blog post includes metadata and SEO fields,
along with content, timing, and categorization.

Fields include:
- A unique title and slug for URL generation and identification.
- HTML content parsed from markdown.
- A Google Drive file ID used as the source of the original content.
- SEO metadata such as meta description and keywords.
- Read time estimate (in minutes) for user experience enhancements.
- Created and updated timestamps for versioning and sitemap accuracy.
- Optional list of categories as JSON for topic grouping.

Columns:
    - id: Primary key, auto-incremented integer.
    - title: Unique title of the blog post (max length 255).
    - slug: URL-friendly string identifier (max length 255).
    - html_content: HTML content of the blog post (text).
    - drive_file_id: Unique Google Drive file ID (max length 255).
    - meta_description: Short SEO-friendly summary (max length 255).
    - keywords: JSON array of SEO keywords.
    - read_time_minutes: Estimated reading time in minutes (integer).
    - categories: JSON array of strings representing categories.
    - created_at: Timestamp of when the post was created (auto-generated).
    - updated_at: Timestamp of the most recent update (auto-updated).
"""

from sqlalchemy import Column, Integer, JSON, MetaData, String, Table, Text, TIMESTAMP, func, text

metadata = MetaData()

blog_posts = Table(
    'blog_posts', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('title', String(255), nullable=False, unique=True),
    Column('slug', String(255), nullable=False, unique=True),
    Column('html_content', Text, nullable=False),
    Column('drive_file_id', String(255), nullable=False, unique=True),
    Column('meta_description', String(255), nullable=False),  # SEO description
    Column('keywords', JSON, nullable=False, default=[]),  # SEO keywords
    Column('read_time_minutes', Integer, nullable=False),  # Estimated reading time
    Column('categories', JSON, nullable=False, default=[]),  # Optional category tags
    Column('created_at', TIMESTAMP(timezone=True), nullable=False, server_default=func.now()),
    Column(
        'updated_at',
        TIMESTAMP(timezone=True),
        server_default=text('CURRENT_TIMESTAMP'),
        onupdate=text('CURRENT_TIMESTAMP'),
        nullable=False
    ),
)
