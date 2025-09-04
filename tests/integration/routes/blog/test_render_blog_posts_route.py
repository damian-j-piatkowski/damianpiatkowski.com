"""Integration tests for the /blog route.

This module verifies the behavior of the blog posts listing page,
particularly focusing on how it handles different states of blog posts
in the database, pagination controls, post content display, and query parameter handling.

Tests included:
    - test_blog_no_posts_message_disappears_when_post_added: Verifies message disappearance when posts exist
    - test_blog_shows_no_posts_message: Verifies empty state message
    - test_custom_per_page_parameter: Tests custom pagination size
    - test_invalid_page_parameter: Verifies handling of invalid page parameters
    - test_pagination_controls_not_shown_with_no_posts: Checks pagination absence without posts
    - test_pagination_controls_not_shown_with_single_page: Checks pagination absence for single page
    - test_pagination_controls_on_last_page: Verifies last page controls state
    - test_pagination_controls_on_middle_page: Verifies middle page controls state
    - test_pagination_controls_with_multiple_pages: Tests pagination with multiple pages
    - test_post_content_truncation: Verifies content truncation in cards
    - test_post_date_formatting: Checks date display formatting
    - test_read_more_links: Verifies correct post link generation

Fixtures:
    - client: Flask test client for making requests
    - session: SQLAlchemy session for DB operations
    - create_blog_post: Factory for creating individual blog post records
    - seed_blog_posts: Factory for creating multiple blog posts at once
"""

import pytest
from bs4 import BeautifulSoup


@pytest.mark.render_blog_posts
def test_blog_no_posts_message_disappears_when_post_added(client, session, create_blog_post):
    """Verifies that the 'No posts' message disappears when a post is added."""
    # First check the empty state
    response = client.get("/blog")
    assert response.status_code == 200
    soup = BeautifulSoup(response.data, 'html.parser')
    assert "No blog posts found yet. Check back soon!" in soup.text

    # Add a blog post
    create_blog_post(
        title="Test Post",
        slug="test-post",
        html_content="<p>Some test content</p>",
        drive_file_id="test123"
    )
    session.commit()

    # Check that the message is gone and post is visible
    response = client.get("/blog")
    assert response.status_code == 200
    soup = BeautifulSoup(response.data, 'html.parser')

    # Message should be gone
    alert = soup.find('div', class_='alert-info')
    assert alert is None

    # Post should be visible
    post_title = soup.find('h5', class_='card-title')
    assert post_title is not None
    assert "Test Post" in post_title.text


@pytest.mark.render_blog_posts
def test_blog_shows_no_posts_message(client, session):
    """Verifies that the blog page shows 'No posts' message when database is empty."""
    response = client.get("/blog")

    assert response.status_code == 200

    # Parse the HTML response
    soup = BeautifulSoup(response.data, 'html.parser')
    alert = soup.find('div', class_='alert-info')

    assert alert is not None
    assert "No blog posts found yet. Check back soon!" in alert.text


@pytest.mark.render_blog_posts
def test_custom_per_page_parameter(client, session, seed_blog_posts):
    """Verifies that custom per_page parameter affects the number of displayed posts."""
    seed_blog_posts(7)
    session.commit()

    response = client.get("/blog?per_page=3")
    soup = BeautifulSoup(response.data, 'html.parser')

    # Should show exactly 3 posts
    posts = soup.find_all('div', class_='blog-post-card')
    assert len(posts) == 3

    # Should have 3 pages (7 posts with 3 per page)
    page_numbers = [item.find('a').text.strip() for item in
                    soup.find_all('li', class_='page-item')
                    if item.find('a').text.strip().isdigit()]
    assert page_numbers == ['1', '2', '3']


@pytest.mark.render_blog_posts
def test_invalid_page_parameter(client, session, seed_blog_posts):
    """Verifies handling of invalid page parameters."""
    seed_blog_posts(5)
    session.commit()

    # Test non-numeric page
    response = client.get("/blog?page=abc")
    assert response.status_code == 200  # Should default to page 1

    # Test negative page
    response = client.get("/blog?page=-1")
    assert response.status_code == 200  # Should default to page 1

    # Test zero page
    response = client.get("/blog?page=0")
    assert response.status_code == 200  # Should default to page 1


@pytest.mark.render_blog_posts
def test_pagination_controls_not_shown_with_no_posts(client, session):
    """Verifies that pagination controls are not shown when there are no posts."""
    response = client.get("/blog")
    assert response.status_code == 200

    soup = BeautifulSoup(response.data, 'html.parser')
    pagination = soup.find('nav', attrs={'aria-label': 'Page navigation'})
    assert pagination is None


@pytest.mark.render_blog_posts
def test_pagination_controls_not_shown_with_single_page(client, session, seed_blog_posts):
    """Verifies that pagination controls are not shown when all posts fit on one page."""
    # Create 5 posts (less than default per_page)
    seed_blog_posts(5)
    session.commit()

    response = client.get("/blog")
    assert response.status_code == 200

    soup = BeautifulSoup(response.data, 'html.parser')
    pagination = soup.find('nav', attrs={'aria-label': 'Page navigation'})
    assert pagination is None


@pytest.mark.render_blog_posts
def test_pagination_controls_on_last_page(client, session, seed_blog_posts):
    """Verifies pagination controls on the last page."""
    seed_blog_posts(25)
    session.commit()

    # Go to last page (page 3)
    response = client.get("/blog?page=3")
    soup = BeautifulSoup(response.data, 'html.parser')

    # Verify active page
    active_page = soup.find('li', class_='page-item active').find('a').text.strip()
    assert active_page == '3'

    # Verify Previous button is enabled
    prev_item = soup.find('a', attrs={'aria-label': 'Previous'}).parent
    assert 'disabled' not in prev_item['class']

    # Verify Next button is disabled
    next_item = soup.find('a', attrs={'aria-label': 'Next'}).parent
    assert 'disabled' in next_item['class']


@pytest.mark.render_blog_posts
def test_pagination_controls_on_middle_page(client, session, seed_blog_posts):
    """Verifies pagination controls on a middle page."""
    seed_blog_posts(25)
    session.commit()

    # Go to page 2
    response = client.get("/blog?page=2")
    soup = BeautifulSoup(response.data, 'html.parser')

    # Verify active page
    active_page = soup.find('li', class_='page-item active').find('a').text.strip()
    assert active_page == '2'

    # Verify both Previous and Next buttons are enabled
    page_items = soup.find_all('li', class_='page-item')
    assert 'disabled' not in page_items[0]['class']  # Previous
    assert 'disabled' not in page_items[-1]['class']  # Next


@pytest.mark.render_blog_posts
def test_pagination_controls_with_multiple_pages(client, session, seed_blog_posts):
    """Verifies pagination controls with multiple pages of posts."""
    # Create enough posts for 3 pages (assuming 10 posts per page)
    seed_blog_posts(25)
    session.commit()

    # Check first page
    response = client.get("/blog")
    soup = BeautifulSoup(response.data, 'html.parser')

    # Verify page numbers
    page_items = soup.find_all('li', class_='page-item')
    page_numbers = [item.find('a').text.strip() for item in page_items
                    if item.find('a').text.strip().isdigit()]
    assert page_numbers == ['1', '2', '3']

    # Verify Previous button is disabled on first page
    prev_button = soup.find('li', class_='page-item disabled').find('a')
    assert prev_button['aria-label'] == 'Previous'

    # Verify Next button is enabled
    next_button = page_items[-1].find('a')
    assert next_button['aria-label'] == 'Next'
    assert 'disabled' not in page_items[-1]['class']


@pytest.mark.render_blog_posts
def test_post_content_truncation(client, session, create_blog_post):
    """Verifies that long post content is properly truncated in the cards."""
    # Create content that will definitely need truncation
    base_text = "This is a very long post content that should be truncated. "
    long_content = f"<p>{base_text * 10}</p>"

    create_blog_post(
        title="Long Post",
        slug="long-post",
        html_content=long_content,
        drive_file_id="test123"
    )
    session.commit()

    response = client.get("/blog")
    soup = BeautifulSoup(response.data, 'html.parser')

    summary_element = soup.find('p', class_='blog-summary')
    assert summary_element is not None, "Summary element not found"

    summary = summary_element.text.strip()
    assert summary, "Summary should not be empty"
    assert len(summary) <= 153, f"Summary too long: {len(summary)} chars"
    assert summary.endswith('...'), f"Summary doesn't end with '...': '{summary}'"
    assert base_text in summary, "Original content not found in summary"


@pytest.mark.render_blog_posts
def test_post_date_formatting(client, session, create_blog_post):
    """Verifies that post dates are properly formatted."""
    from datetime import datetime

    test_date = datetime(2024, 7, 16, 14, 30, 0)
    create_blog_post(
        title="Date Test Post",
        slug="date-test",
        html_content="<p>Some test content</p>",
        drive_file_id="test123",
        created_at=test_date
    )
    session.commit()

    response = client.get("/blog")
    soup = BeautifulSoup(response.data, 'html.parser')

    # Find element with all three classes
    date_element = soup.find('p', class_=lambda x: x and all(c in x for c in ['card-text', 'text-muted', 'small']))
    date_text = date_element.text.strip()
    assert date_text == "July 16, 2024"


@pytest.mark.render_blog_posts
def test_read_more_links(client, session, create_blog_post):
    """Verifies that 'Read More' links point to correct single post URLs."""
    create_blog_post(
        title="Test Post",
        slug="test-post",
        html_content="<p>Some test content</p>",
        drive_file_id="test123"
    )
    session.commit()

    response = client.get("/blog")
    soup = BeautifulSoup(response.data, 'html.parser')

    read_more_link = soup.find('a', class_='btn-custom-green')
    assert read_more_link['href'] == "/blog/test-post"
