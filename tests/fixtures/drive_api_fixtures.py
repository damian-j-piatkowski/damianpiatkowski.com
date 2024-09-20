#todo docstring (main chatgpt)

# drive_api_fixtures.py

from typing import List, Dict
import pytest

@pytest.fixture
def mock_drive_docs() -> List[Dict[str, str]]:
    """Fixture to create mock Google Drive documents."""
    return [
        {'name': 'Post 1'},
        {'name': 'Post 2'},
        {'name': 'Post 4'},  # Post 4 is in Drive but not in DB
    ]