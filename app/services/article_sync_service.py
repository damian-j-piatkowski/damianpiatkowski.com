"""Module for comparing blog posts in the database with documents in Drive.

This module provides functionality to find missing articles that exist
in Google Drive but are not yet present in the blog posts table in the database.
"""

from typing import List

def find_missing_articles(
        db_titles: List[str],  # Expects already normalized titles from DB
        drive_titles: List[str]  # Expects normalized titles from Drive
) -> List[str]:
    """Compare normalized blog post titles from the database with normalized document titles from Google Drive.

    Serves to identify missing articles.

    Args:
        db_titles (List[str]): A list of normalized blog post titles fetched from the database.
        drive_titles (List[str]): A list of normalized document titles from Google Drive.

    Returns:
        List[str]: A list of titles for documents that exist in Google Drive
            but are not present in the database.
    """
    # Find documents in Drive that are not in the DB
    missing_articles = set(drive_titles) - set(db_titles)

    return list(missing_articles)
