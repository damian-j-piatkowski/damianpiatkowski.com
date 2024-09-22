# todo finish (main chatgpt)

import pytest
from typing import List, Dict
from unittest.mock import MagicMock
from app.domain.blog_post import BlogPost
from app.services.article_sync_service import find_missing_articles



def test_find_missing_articles_no_missing(mock_db_posts, mock_drive_docs):
    """Test case where all Google Drive docs are in the database."""
    # Use the same titles in db_posts and drive_docs
    mock_drive_docs_same_titles = [{'name': post.title} for post in
                                   mock_db_posts]

    missing_articles = find_missing_articles(mock_db_posts,
                                             mock_drive_docs_same_titles)
    assert missing_articles == []


def test_find_missing_articles_with_missing(mock_db_posts, mock_drive_docs):
    """Test case where some Google Drive docs are not in the database."""
    missing_articles = find_missing_articles(mock_db_posts, mock_drive_docs)

    assert missing_articles == ['Post 4']


def test_find_missing_articles_no_docs_in_drive(mock_db_posts):
    """Test case where there are no documents in Google Drive."""
    mock_empty_drive_docs = []

    missing_articles = find_missing_articles(mock_db_posts,
                                             mock_empty_drive_docs)
    assert missing_articles == []


def test_find_missing_articles_no_posts_in_db(mock_drive_docs):
    """Test case where there are no blog posts in the database."""
    mock_empty_db_posts = []

    missing_articles = find_missing_articles(mock_empty_db_posts,
                                             mock_drive_docs)

    assert set(missing_articles) == {'Post 1', 'Post 2', 'Post 4'}
