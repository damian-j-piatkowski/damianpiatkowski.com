"""Service for content formatting and manipulation.

This module provides utilities for transforming and manipulating content in various formats,
particularly focusing on blog post content processing. It includes:

1. Markdown to HTML conversion:
   - Advanced markdown features support through Python-Markdown
   - Code syntax highlighting
   - Tables, footnotes, and other technical writing elements
   - Configurable extensions system

2. Content manipulation:
   - Text truncation for previews
   - Smart ellipsis handling
   - Empty content handling

3. Date formatting:
   - Conversion of datetime strings from the database into human-readable formats
   - Graceful fallback if parsing fails

The module uses the Python-Markdown library with carefully selected
extensions to ensure proper rendering of code blocks, tables, and other
markdown elements commonly used in technical blog posts.

Typical usage example:
    html_content = convert_markdown_to_html("# Title\nContent")
    preview = trim_content(html_content, max_length=100)
    formatted_date = format_date("2025-07-22 07:39:58")

Functions:
    convert_markdown_to_html: Transforms markdown text to HTML with enhanced features
    trim_content: Creates preview versions of content by trimming to specified length
    format_date: Converts datetime strings into human-readable formats
"""

from typing import List, Optional
from datetime import datetime
import markdown


def convert_markdown_to_html(markdown_text: str, extensions: Optional[List[str]] = None) -> str:
    """Converts markdown-formatted text to HTML with enhanced features.

    Supports advanced markdown features like:
    - Fenced code blocks with syntax highlighting
    - Tables
    - Line breaks
    - Task lists
    - Table of contents
    - Definition lists
    - Footnotes

    Args:
        markdown_text: The article content in markdown format.
        extensions: Optional list of additional markdown extensions to use.
            Defaults to None, using the standard set of extensions.

    Returns:
        The HTML content ready for storage in the blog_posts table.
    """
    # Remove BOM if present
    markdown_text = markdown_text.lstrip('\ufeff')

    # Default extensions for technical blog posts
    default_extensions = [
        'fenced_code',
        'codehilite',
        'tables',
        'toc',
        'def_list',
        'footnotes',
        'md_in_html',
        'sane_lists',
        'smarty',
        'attr_list'
    ]

    all_extensions = default_extensions + (extensions or [])

    extension_configs = {
        'codehilite': {
            'css_class': 'highlight',
            'use_pygments': True,
            'noclasses': False,
            'linenums': False
        },
        'toc': {
            'permalink': True,
            'baselevel': 1
        }
    }

    return markdown.markdown(
        markdown_text,
        extensions=all_extensions,
        extension_configs=extension_configs,
        output_format='html'
    )


def trim_content(content: str, max_length: int = 200) -> str:
    """Trims the content to a maximum length for preview purposes.

    Args:
        content (str): The full content to be trimmed.
        max_length (int): The maximum number of characters to keep.

    Returns:
        str: The trimmed content with an ellipsis if truncated.
    """
    if not content:
        return ""
    if len(content) > max_length:
        return content[:max_length].rstrip() + "..."
    return content


def format_date(date_str: str) -> str:
    """Converts a datetime string from the database into a human-readable format.

    Example:
        "2025-07-22 07:39:58" -> "July 22, 2025"

    Falls back to YYYY-MM-DD if parsing fails.

    Args:
        date_str (str): Datetime string in '%Y-%m-%d %H:%M:%S' format.

    Returns:
        str: A human-readable formatted date string.
    """
    if not date_str:
        return ""
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        return dt.strftime('%B %d, %Y')
    except ValueError:
        return date_str[:10]
