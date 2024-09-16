"""Utility pytest fixtures for setting up and managing test environments.

This module includes fixtures that are used across various tests, such as
cleaning up the download directory, providing standard test data structures,
and handling form submissions for testing.

Fixtures:
    - clean_download_dir: Cleans up specific files (e.g., PDFs) in the download
        directory before and after tests.
    - incomplete_form_data: Provides incomplete form data for testing
        validation.
    - valid_form_data: Provides valid form data for contact form submission.
    - valid_log_data: Provides valid log data for schema validation tests.
"""

import os
from pathlib import Path

import pytest


@pytest.fixture(scope='function')
def clean_download_dir() -> Path:
    """Cleans up the download directory by removing specific files.

    This fixture ensures that both the `.pdf` and `.crdownload` files related
    to the resume are removed before the test begins and also ensures cleanup
    after the test ends.

    Yields:
        Path: The path to the resume `.pdf` file in the download directory.
    """
    download_directory = os.getenv("DOWNLOAD_DIRECTORY", "/tmp")
    resume_file = Path(download_directory) / "resume.pdf"
    crdownload_file = Path(download_directory) / "resume.pdf.crdownload"

    # Setup: Remove the .pdf and .crdownload files if they exist before the test
    for file in [resume_file, crdownload_file]:
        if file.exists():
            file.unlink()

    # Yield the resume file path for use in the test
    yield resume_file

    # Teardown: Remove both files after the test
    for file in [resume_file, crdownload_file]:
        if file.exists():
            file.unlink()


@pytest.fixture(scope='function')
def incomplete_form_data():
    """Fixture providing incomplete form data for contact form tests.

    This fixture returns a dictionary with missing or incomplete data to be used
    in tests that check form validation and error handling.
    """
    return {
        'name': '',
        'email': 'john@example.com',
        'message': 'This is a test message.'
    }


@pytest.fixture(scope='function')
def valid_form_data():
    """Fixture providing valid form data for contact form submission tests.

    This fixture returns a dictionary with complete and valid form data, which
    can be used in tests to simulate successful form submissions.
    """
    return {
        'name': 'John Doe',
        'email': 'john@example.com',
        'message': 'This is a test message.'
    }


@pytest.fixture(scope='function')
def valid_log_data():
    """Fixture providing valid log data.

    This fixture returns a dictionary containing log data with
    typical values used for testing the log schema validation.
    """
    return {
        "level": "INFO",
        "message": "This is a log message."
    }
