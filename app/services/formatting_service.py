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

The module uses the Python-Markdown library with carefully selected
extensions to ensure proper rendering of code blocks, tables, and other
markdown elements commonly used in technical blog posts.

Typical usage example:
    html_content = convert_markdown_to_html("# Title\nContent")
    preview = trim_content(html_content, max_length=100)

Functions:
    convert_markdown_to_html: Transforms markdown text to HTML with enhanced features
    trim_content: Creates preview versions of content by trimming to specified length
"""

from typing import List, Optional

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
        'fenced_code',  # Code blocks with language specification
        'codehilite',  # Syntax highlighting
        'tables',  # Markdown tables
        'toc',  # Table of contents
        'def_list',  # Definition lists
        'footnotes',  # Footnotes support
        'md_in_html',  # Allow markdown inside HTML
        'sane_lists',  # Better list handling
        'smarty',  # Smart quotes, dashes, etc.
        'attr_list'  # Add HTML attributes to elements
    ]

    # Combine default and custom extensions
    all_extensions = default_extensions + (extensions or [])

    # Extension configuration
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

    # Convert markdown to HTML with configured extensions
    html_content = markdown.markdown(
        markdown_text,
        extensions=all_extensions,
        extension_configs=extension_configs,
        output_format='html'
    )

    return html_content


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
