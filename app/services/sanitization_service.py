"""Service for sanitizing user input and HTML content.

This module provides functionality to normalize titles, sanitize contact form input, 
and clean HTML content to prevent XSS attacks.
"""

import re
from typing import Dict

from bleach import clean


def extract_slug_and_title(file_name: str) -> tuple[str, str]:
    """Extracts a slug and title from a Google Drive file name, enforcing numeric prefixes.

    - Numeric prefix (e.g., "01_") is required but removed in the final output.
    - The first `_` is replaced with `-`, and all remaining `_` are converted to `-`.
    - Extra spaces are trimmed and normalized.
    - The final slug is always kebab-case (lowercase, hyphenated).
    - The title is in title case.

    Args:
        file_name (str): The file name to process.

    Returns:
        tuple[str, str]: A tuple containing:
            - The slug (str) → Derived from the file name with hyphens.
            - The title (str) → The human-readable version in title case.

    Raises:
        ValueError: If the file name does not start with a numeric prefix followed by `_`.

    Examples:
        >>> extract_slug_and_title("01_hello_world.md")
        ("hello-world", "Hello World")

        >>> extract_slug_and_title("02_another-post.txt")
        ("another-post", "Another Post")
    """
    # Ensure the file name starts with a numeric prefix followed by `_` or `-`
    if not re.match(r'^\d+[-_]', file_name):
        raise ValueError(f"Invalid file name format: '{file_name}'. Expected a prefix separated by '-'.")

    # Normalize prefix separator to always be `-`
    file_name = re.sub(r'^(\d+)_', r'\1-', file_name)

    # Remove numeric prefix (e.g., "08-" from "08-messy-file-name")
    file_name = re.sub(r'^\d+-', '', file_name)

    # Remove file extension if present
    title_without_ext = file_name.rsplit('.', 1)[0]

    # Normalize spaces (remove leading/trailing and replace multiple spaces with a single space)
    title_without_ext = re.sub(r'\s+', ' ', title_without_ext.strip())

    # Convert all remaining underscores to hyphens for slug consistency
    title_without_ext = title_without_ext.replace('_', '-')

    # Generate slug: lowercase + hyphenate (no underscores)
    slug = title_without_ext.replace(' ', '-').lower()

    # Convert title to title case
    title = title_without_ext.replace('-', ' ').title()

    return slug, title


def sanitize_contact_form_input(form_data: Dict[str, str]) -> Dict[str, str]:
    """Dynamically sanitize all fields in the contact form to prevent XSS attacks."""
    sanitized_data = {}

    for field, value in form_data.items():
        # Ensure value is a string, if not convert to string or set to empty
        if value is None:
            value = ""
        else:
            value = str(value)

        # Remove <script> tags and their content using regex
        value = re.sub(r'<script.*?>.*?</script>', '', value, flags=re.DOTALL)

        # Use Bleach to remove all remaining tags and attributes
        sanitized_value = clean(value, tags=[], attributes={}, protocols=[], strip=True)

        # Strip extra newlines and spaces
        sanitized_data[field] = sanitized_value.strip()

    return sanitized_data


def sanitize_html(content: str) -> str:
    """Sanitizes HTML content to prevent XSS attacks while preserving formatted text.

    Performs the following sanitization steps:
    1. Removes dangerous <script> tags and their content
    2. Filters HTML to allow only safe tags for blog content
    3. Normalizes whitespace and formatting (but preserves code block formatting)
    4. Removes pilcrow symbols (¶) from headings

    Args:
        content: Raw HTML content to be sanitized.

    Returns:
        Sanitized HTML content with preserved formatting and structure.

    Example:
        >>> sanitize_html('<h1>Title</h1><script>alert("xss")</script><p>Content</p>')
        '<h1>Title</h1><p>Content</p>'
    """
    # Remove <script> tags and their content using regex
    content = re.sub(r'\s*<script.*?>.*?</script>\s*', '', content, flags=re.DOTALL)

    # Remove pilcrow symbols (¶) and related permalink anchors
    content = re.sub(r'<a[^>]*class="[^"]*pilcrow[^"]*"[^>]*>.*?</a>', '', content)
    content = re.sub(r'¶', '', content)
    content = re.sub(r'&para;', '', content)

    # Use Bleach to sanitize remaining HTML, allowing only safe tags
    allowed_tags = [
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',  # Headers
        'p', 'br',  # Paragraphs and line breaks
        'b', 'strong', 'i', 'em',  # Text emphasis
        'ul', 'ol', 'li',  # Lists
        'pre', 'code',  # Code blocks
        'blockquote', 'q',  # Quotes
        'table', 'thead', 'tbody', 'tr',  # Tables
        'th', 'td',
        'a', 'img',  # Links and images
        'sup', 'sub'  # Superscript/subscript
    ]

    sanitized_content = clean(
        content,
        tags=allowed_tags,
        attributes={
            'a': ['href', 'title'],
            'img': ['src', 'alt', 'title']
        },
        strip=True
    )

    # Extract code blocks before whitespace normalization to preserve their formatting
    code_blocks = []
    def preserve_code_block(match):
        placeholder = f"__CODE_BLOCK_{len(code_blocks)}__"
        code_blocks.append(match.group(0))
        return placeholder

    # Temporarily replace code blocks with placeholders
    sanitized_content = re.sub(r'<pre><code>.*?</code></pre>', preserve_code_block, sanitized_content, flags=re.DOTALL)

    # Now safely normalize whitespace outside of code blocks
    sanitized_content = re.sub(r'\s+</', '</', sanitized_content)  # Trim space before closing tags
    sanitized_content = re.sub(r'>\s+<', '><', sanitized_content)  # Remove spaces between tags
    sanitized_content = re.sub(r'\s{2,}', ' ', sanitized_content)  # Collapse multiple spaces

    # Restore code blocks with their original formatting
    for i, code_block in enumerate(code_blocks):
        sanitized_content = sanitized_content.replace(f"__CODE_BLOCK_{i}__", code_block)

    return sanitized_content.strip()
