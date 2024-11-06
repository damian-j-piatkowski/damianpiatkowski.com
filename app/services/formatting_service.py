import markdown

def convert_markdown_to_html(markdown_text: str) -> str:
    """
    Converts a markdown-formatted article to HTML.

    Args:
        markdown_text (str): The article content in markdown format.

    Returns:
        str: The HTML content that can be stored in the blog_posts table.
    """
    # Initialize markdown with extensions for code highlighting and other features
    html_content = markdown.markdown(
        markdown_text,
        extensions=['fenced_code', 'codehilite', 'tables']
    )
    return html_content
