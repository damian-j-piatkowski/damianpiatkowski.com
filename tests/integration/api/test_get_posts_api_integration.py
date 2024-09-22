# Integration tests for API blog route (tests/integration/test_api_blog_route.py)

def test_get_posts_success(client, create_blog_post, session):
    """
    Test the /api/posts route with actual blog posts in the database.
    """
    # Create sample blog posts using the fixture
    post1 = create_blog_post(title='Post 1', content='Content 1', url='post-1')
    post2 = create_blog_post(title='Post 2', content='Content 2', url='post-2')
    session.commit()

    # Perform a GET request to the API route
    response = client.get('/api/posts')

    # Assert that the response is successful
    assert response.status_code == 200

    # Check if the response data contains the correct posts
    data = response.get_json()
    assert len(data) == 2
    assert data[0]['title'] == 'Post 1'
    assert data[1]['title'] == 'Post 2'

def test_get_posts_empty(client, session):
    """
    Test the /api/posts route when no blog posts exist in the database.
    """
    # Perform a GET request to the API route
    response = client.get('/api/posts')

    # Assert that the response is a 404 and that the correct message is returned
    assert response.status_code == 404
    assert response.get_json() == {"message": "No blog posts found"}
