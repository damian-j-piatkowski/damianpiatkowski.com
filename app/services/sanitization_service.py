"""Service for sanitizing user input and HTML content.

This module provides functionality to normalize titles, sanitize contact form input, 
and clean HTML content to prevent XSS attacks.
"""

import re
from typing import Dict

from bleach import clean


def normalize_title(title: str) -> str:
    """Normalize a title by stripping prefixes like '01_'.

    Args:
        title (str): The title to be normalized.

    Returns:
        str: The normalized title with any prefix removed.

    Raises:
        ValueError: If the title does not contain a valid prefix.
    """
    if '_' not in title:
        raise ValueError(f"Invalid title format: '{title}'. Expected a prefix separated by '_'.")

    return title.split('_', 1)[1]


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
    """Sanitize the HTML content to prevent XSS attacks.

    Args:
        content (str): The HTML content to be sanitized.

    Returns:
        str: The sanitized HTML content.
    """
    # Remove <script> tags and their content using regex, ensuring surrounding spaces are reduced
    content = re.sub(r'\s*<script.*?>.*?</script>\s*', '', content, flags=re.DOTALL)

    # Use Bleach to sanitize remaining HTML, allowing only safe tags
    sanitized_content = clean(content, tags=['p', 'b', 'i', 'ul', 'li'], strip=True)

    # Remove extra spaces before closing tags and collapse excess spaces between tags
    sanitized_content = re.sub(r'\s+</', '</', sanitized_content)  # Trim space before closing tags
    sanitized_content = re.sub(r'>\s+<', '><', sanitized_content)  # Remove spaces between tags
    sanitized_content = re.sub(r'\s{2,}', ' ',
                               sanitized_content)  # Collapse multiple spaces to a single space

    return sanitized_content.strip()  # Return the trimmed result

