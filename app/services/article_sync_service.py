"""Module for comparing blog posts in the database with documents in Drive.

This module provides functionality to find missing articles that exist
in Google Drive but are not yet present in the blog posts table in the database.
"""

from typing import List, Dict

from app.domain.blog_post import BlogPost


def find_missing_articles(
        db_posts: List[BlogPost],
        drive_docs: List[Dict[str, str]]
) -> List[str]:
    """Compare blog posts from the database with documents from Google Drive.

    Serves to identify missing articles.

    Args:
        db_posts (List[object]): A list of blog post objects fetched from the
            database. Each post object should have a 'title' attribute.
        drive_docs (List[Dict[str, str]]): A list of documents from Google
            Drive, where each document is represented as a dictionary
            containing at least a 'name' key for the title.

    Returns:
        List[str]: A list of titles for documents that exist in Google Drive
            but are not present in the database.
    """
    # Extract the titles from the database blog posts
    db_titles = {post.title for post in db_posts}

    # Extract the names (titles) from Google Drive documents
    drive_titles = {doc['name'] for doc in drive_docs}

    # Find documents in Drive that are not in the DB
    missing_articles = drive_titles - db_titles

    return list(missing_articles)
