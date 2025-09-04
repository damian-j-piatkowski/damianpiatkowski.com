"""Service for content formatting and manipulation.

This module provides utilities for transforming and manipulating content in various formats,
particularly focusing on blog post content processing. It includes:

1. Markdown to HTML conversion:
   - Advanced markdown features support through Python-Markdown
   - Code syntax highlighting
   - Tables, footnotes, and other technical writing elements
   - Configurable extensions system

2. Date formatting:
   - Conversion of datetime strings from the database into human-readable formats
   - Graceful fallback if parsing fails

3. Content manipulation:
   - Text truncation for previews
   - Smart ellipsis handling
   - Empty content handling

Functions:
    convert_markdown_to_html: Transforms markdown text to HTML with enhanced features
    format_date: Converts datetime strings into human-readable formats
    trim_content: Creates preview versions of content by trimming to specified length
"""

import logging
from datetime import datetime
from typing import List, Optional

import markdown

logger = logging.getLogger(__name__)


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
    logger.debug("convert_markdown_to_html: Starting conversion. Input length=%d", len(markdown_text or ""))

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
    logger.debug("convert_markdown_to_html: Using extensions=%s", all_extensions)

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

    html = markdown.markdown(
        markdown_text,
        extensions=all_extensions,
        extension_configs=extension_configs,
        output_format='html'
    )

    logger.debug("convert_markdown_to_html: Conversion complete. Output length=%d", len(html or ""))
    return html


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
        logger.debug("format_date: Empty date string received.")
        return ""
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        formatted = dt.strftime('%B %d, %Y')
        logger.debug("format_date: Parsed '%s' -> '%s'", date_str, formatted)
        return formatted
    except ValueError:
        logger.warning("format_date: Failed to parse '%s', using fallback.", date_str)
        fallback = date_str[:10] if len(date_str) >= 10 else date_str
        logger.debug("format_date: Fallback result='%s'", fallback)
        return fallback


def trim_content(content: str, max_length: int = 200) -> str:
    """Trims the content to a maximum length for preview purposes.

    Args:
        content (str): The full content to be trimmed.
        max_length (int): The maximum number of characters to keep.

    Returns:
        str: The trimmed content with an ellipsis if truncated.
    """
    if not content:
        logger.debug("trim_content: Empty content received.")
        return ""
    if len(content) > max_length:
        trimmed = content[:max_length].rstrip() + "..."
        logger.debug(
            "trim_content: Content truncated from length=%d to length=%d",
            len(content), len(trimmed)
        )
        return trimmed
    logger.debug("trim_content: No truncation needed. Length=%d", len(content))
    return content
