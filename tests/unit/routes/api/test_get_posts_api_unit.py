from unittest.mock import patch

from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError


def test_get_posts_success(client):
    """Tests that the /api/posts route returns a successful response."""
    with patch('app.routes.api.blog.get_all_posts') as mock_get_all_posts:
        # Mock the controller to return a list of blog posts
        mock_get_all_posts.return_value = jsonify([
            {'title': 'Post 1', 'content': 'Content of post 1'},
            {'title': 'Post 2', 'content': 'Content of post 2'}
        ]), 200

        # Perform a GET request to the API route
        response = client.get('/api/posts')

        # Assert that the response is 200 OK and contains the mock data
        assert response.status_code == 200
        assert response.json == [
            {'title': 'Post 1', 'content': 'Content of post 1'},
            {'title': 'Post 2', 'content': 'Content of post 2'}
        ]


def test_get_posts_sqlalchemy_error(client):
    """
    Test that the /api/posts route handles SQLAlchemyError correctly.
    """
    with patch('app.routes.api.blog.get_all_posts') as mock_get_all_posts:
        # Mock the controller to raise SQLAlchemyError
        mock_get_all_posts.side_effect = SQLAlchemyError('Database failure')

        # Perform a GET request to the API route
        response = client.get('/api/posts')

        # Assert that the response is 500 for database error
        assert response.status_code == 500
        assert response.json == {
            'error': 'Database error',
            'details': 'Database failure'
        }


def test_get_posts_unexpected_error(client):
    """
    Test that the /api/posts route handles unexpected errors correctly.
    """
    with patch('app.routes.api.blog.get_all_posts') as mock_get_all_posts:
        # Mock the controller to raise a general Exception
        mock_get_all_posts.side_effect = Exception('Unexpected failure')

        # Perform a GET request to the API route
        response = client.get('/api/posts')

        # Assert that the response is 500 for an unexpected error
        assert response.status_code == 500
        assert response.json == {
            'error': 'Unexpected error',
            'message': 'Unexpected failure'
        }


def test_get_posts_value_error(client):
    """
    Test that the /api/posts route handles ValueError correctly.
    """
    with patch('app.routes.api.blog.get_all_posts') as mock_get_all_posts:
        # Mock the controller to raise ValueError
        mock_get_all_posts.side_effect = ValueError('Invalid value')

        # Perform a GET request to the API route
        response = client.get('/api/posts')

        # Assert that the response is 400 for invalid value
        assert response.status_code == 400
        assert response.json == {
            'error': 'Invalid value',
            'message': 'Invalid value'
        }
