import markdown

def convert_markdown_to_html(markdown_text: str) -> str:
    """
    Converts a markdown-formatted article to HTML.

    Args:
        markdown_text (str): The article content in markdown format.

    Returns:
        str: The HTML content that can be stored in the blog_posts table.
    """
    markdown_text = markdown_text.lstrip('\ufeff')
    # Initialize markdown with extensions for code highlighting and other features
    html_content = markdown.markdown(
        markdown_text,
        extensions=['fenced_code', 'codehilite', 'tables', 'nl2br']
    )

    return html_content

def trim_content(content: str, max_length: int = 200) -> str:
    """
    Trims the content to a maximum length for preview purposes.

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
