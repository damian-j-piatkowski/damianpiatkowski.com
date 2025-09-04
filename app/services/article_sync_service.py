"""Module for comparing blog posts in the database with documents in Drive.

This module provides functionality to find missing articles that exist
in Google Drive but are not yet present in the blog posts table in the database.
"""

from typing import Set, List

def find_missing_articles(db_titles: list[str], drive_titles: list[str]) -> list[str]:
    """
    Compare titles from the database with titles from Google Drive to find missing articles.

    Args:
        db_titles (list[str]): List of normalized titles from the database.
        drive_titles (list[str]): List of normalized titles from Google Drive.

    Returns:
        list[str]: List of titles in Google Drive that are not in the database.
    """
    # Convert lists to sets for set difference operation
    db_title_set = set(db_titles)
    drive_title_set = set(drive_titles)

    # Find titles in Drive that are not in the database
    missing_titles = drive_title_set - db_title_set

    # Convert the result back to a list
    return list(missing_titles)
