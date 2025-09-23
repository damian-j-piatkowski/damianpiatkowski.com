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
import re
from datetime import datetime
from typing import Optional, List

import markdown
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def convert_markdown_to_html(markdown_text: str, extensions: Optional[List[str]] = None) -> str:
    """Converts markdown-formatted text to HTML with enhanced features.

    Customizations:
    - Wraps '#damianpiatkowski.com#' in <span class="site-ref"> for styling
    - Adds 'link' class to all <a> tags, except auto-generated heading permalinks (class="headerlink")
    - Formats blockquote attribution into:
        <footer class="attribution"><span class="author">Author</span>, <em class="book">Book Title</em></footer>
      Rules:
        * If there is additional attribution text after the author (e.g., "quoted in …"), it is preserved after the comma.
        * If there is only a trailing comma before the book title, the comma is preserved.
    """
    logger.debug("convert_markdown_to_html: Starting conversion. Input length=%d", len(markdown_text or ""))

    markdown_text = markdown_text.lstrip('\ufeff')

    default_extensions = [
        "fenced_code",
        "tables",
        "toc",
        "def_list",
        "footnotes",
        "md_in_html",
        "sane_lists",
        "smarty",
        "attr_list",
    ]

    all_extensions = default_extensions + (extensions or [])
    extension_configs = {"toc": {"permalink": True, "baselevel": 1}}

    # Convert Markdown
    html = markdown.markdown(
        markdown_text,
        extensions=all_extensions,
        extension_configs=extension_configs,
        output_format="html",
    )

    soup = BeautifulSoup(html, "html.parser")

    # --- Style links ---
    for a in soup.find_all("a", href=True):
        if "headerlink" in a.get("class", []):
            continue  # skip permalinks
        a["class"] = (a.get("class", []) + ["link"])

    # --- Wrap '#damianpiatkowski.com#' in <span> ---
    domain_pattern = re.compile(r"#(damianpiatkowski\.com)#", re.IGNORECASE)
    for node in soup.find_all(string=True):
        if domain_pattern.search(node):
            new_html = domain_pattern.sub(
                r'<span class="site-ref">\1</span>', node
            )
            new_nodes = BeautifulSoup(new_html, "html.parser")
            node.replace_with(new_nodes)

    # --- Blockquote attribution ---
    for bq in soup.find_all("blockquote"):
        p_tags = bq.find_all("p")
        if not p_tags:
            continue
        last_p = p_tags[-1]

        if last_p.find("em"):  # looks like an attribution
            book_tag = last_p.find("em")

            # Extract text parts before and after <em>
            before_em = []
            after_em = []
            seen_book = False
            for c in last_p.contents:
                if c == book_tag:
                    seen_book = True
                    continue
                if not seen_book:
                    before_em.append(c)
                else:
                    after_em.append(c)

            # First chunk of before_em = author (first phrase before comma)
            before_text = "".join(str(c) for c in before_em).strip()

            if "," in before_text:
                parts = [p.strip() for p in before_text.split(",", 1)]
                author_text = parts[0]
                rest_text = parts[1] if len(parts) > 1 and parts[1] else None
                had_comma = True
            else:
                author_text, rest_text = before_text, None
                had_comma = False

            # Build footer
            new_footer = soup.new_tag("footer", attrs={"class": "attribution"})

            author_tag = soup.new_tag("span", attrs={"class": "author"})
            author_tag.string = author_text
            new_footer.append(author_tag)

            if rest_text:  # case: "Naval Ravikant, quoted in …"
                new_footer.append(", " + rest_text)
            elif had_comma:  # case: "Austin Kleon," (just a trailing comma)
                new_footer.append(",")

            new_footer.append(" ")
            new_footer.append(book_tag)

            if after_em:
                new_footer.append(" " + "".join(str(c) for c in after_em).strip())

            last_p.replace_with(new_footer)

    html = str(soup)
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
