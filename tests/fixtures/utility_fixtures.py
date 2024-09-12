"""Utility pytest fixtures for setting up and managing test environments.

This module includes fixtures that clean up the download directory before
and after tests. It ensures the specified files (like PDFs) are removed before
the test starts and after the test ends.

Fixtures:
    - clean_download_dir: Cleans up specific files (e.g., PDFs) in the download
        directory before and after tests.
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
