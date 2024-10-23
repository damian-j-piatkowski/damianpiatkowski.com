"""Unit tests for the find_missing_articles function of the ArticleSyncService module.

This module contains unit tests for the find_missing_articles function, which compares
blog post titles from the database with document titles from Google Drive to identify
missing articles.

Tests included:
    - test_find_missing_articles_with_missing_articles: Verifies that missing articles
      are correctly identified when there are titles in Google Drive but not in the database.
    - test_find_missing_articles_with_no_missing_articles: Verifies that an empty list
      is returned when all articles in Google Drive are already in the database.
    - test_find_missing_articles_with_empty_db: Verifies that all Drive titles are
      returned as missing when the database has no articles.
    - test_find_missing_articles_with_empty_drive: Verifies that an empty list is returned
      when there are no titles in Google Drive.

Mocks:
    - None required, as this function performs pure logic with no external dependencies.
"""

import pytest

from app.services.article_sync_service import find_missing_articles


@pytest.fixture
def sample_db_titles() -> list[str]:
    """Fixture providing a sample list of normalized titles from the database."""
    return ["introduction-to-python", "flask-for-beginners", "unit-testing-with-pytest"]


@pytest.fixture
def sample_drive_titles() -> list[str]:
    """Fixture providing a sample list of normalized titles from Google Drive."""
    return ["introduction-to-python", "flask-for-beginners", "working-with-google-drive-api"]


def test_find_missing_articles_with_missing_articles(
        sample_db_titles: list[str], sample_drive_titles: list[str]) -> None:
    """Tests that missing articles are identified when Drive has titles not in the database."""
    # Act
    missing_articles = find_missing_articles(sample_db_titles, sample_drive_titles)

    # Assert
    assert missing_articles == ["working-with-google-drive-api"]


def test_find_missing_articles_with_no_missing_articles(
        sample_db_titles: list[str]) -> None:
    """Tests that no missing articles are identified when all Drive titles are in the database."""
    # Arrange
    drive_titles = ["introduction-to-python", "flask-for-beginners", "unit-testing-with-pytest"]

    # Act
    missing_articles = find_missing_articles(sample_db_titles, drive_titles)

    # Assert
    assert missing_articles == []


def test_find_missing_articles_with_empty_db(
        sample_drive_titles: list[str]) -> None:
    """Tests that all Drive titles are returned as missing when the database is empty."""
    # Arrange
    db_titles = []  # No articles in the database

    # Act
    missing_articles = find_missing_articles(db_titles, sample_drive_titles)

    # Assert
    assert missing_articles == sample_drive_titles


def test_find_missing_articles_with_empty_drive(
        sample_db_titles: list[str]) -> None:
    """Tests that no missing articles are identified when there are no titles in Google Drive."""
    # Arrange
    drive_titles = []  # No documents in Google Drive

    # Act
    missing_articles = find_missing_articles(sample_db_titles, drive_titles)

    # Assert
    assert missing_articles == []
