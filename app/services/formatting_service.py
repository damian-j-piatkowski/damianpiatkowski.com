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
