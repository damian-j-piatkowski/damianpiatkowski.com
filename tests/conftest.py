import logging
import os
from pathlib import Path

import pytest
from selenium import webdriver

from app import create_app, db
from sqlalchemy.orm import sessionmaker, scoped_session
from app.models.blog_post import metadata as blog_post_metadata
from app.models.log import metadata as log_metadata

all_metadata = [blog_post_metadata, log_metadata]


@pytest.fixture(scope='session')
def app():
    """Session-wide test Flask application."""
    app = create_app()
    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture(scope='module')
def _db(app):
    """Session-wide test database."""
    with app.app_context():
        # Create all tables
        for metadata in all_metadata:
            metadata.create_all(bind=db.engine)
        yield db
        # Drop all tables
        for metadata in all_metadata:
            metadata.drop_all(bind=db.engine)


@pytest.fixture(scope='function')
def session(_db):
    """Creates a new database session for a test."""
    connection = _db.engine.connect()
    transaction = connection.begin()

    # Create a configured "Session" class
    session_factory = sessionmaker(bind=connection)
    # Create a scoped session
    test_session = scoped_session(session_factory)

    _db.session = test_session

    yield test_session

    transaction.rollback()
    connection.close()
    test_session.remove()


@pytest.fixture
def clean_download_dir():
    resume_file = Path.home() / "Downloads" / "resume.pdf"

    # Setup: Ensure the download directory is clean before the test
    if os.path.exists(resume_file):
        os.remove(resume_file)

    yield resume_file

    # Teardown: Remove the file after the test completes
    if os.path.exists(resume_file):
        os.remove(resume_file)


@pytest.fixture(scope="module", params=[
    {'width': 375, 'height': 667},  # Mobile
    {'width': 768, 'height': 1024},  # Tablet
    {'width': 1366, 'height': 768},  # Laptop
    {'width': 1920, 'height': 1080},  # Big monitor
    {
        'width': 1080, 'height': 2400,
        'user_agent': ('Mozilla/5.0 (Linux; Android 13; Pixel 7) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/91.0.4472.77 Mobile Safari/537.36')
    }  # Pixel 7
])
def driver(request):
    options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": os.getenv('DOWNLOAD_DIRECTORY', '/tmp'),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument('--headless')  # Ensure tests can run without a UI
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    if 'user_agent' in request.param:
        options.add_argument(f"user-agent={request.param['user_agent']}")
    driver = None  # Initialize driver variable
    try:
        driver = webdriver.Chrome(options=options)
        driver.set_window_size(request.param['width'], request.param['height'])
        yield driver
    finally:
        if driver is not None:
            driver.quit()


def capture_screenshot(driver, name):
    screenshots_dir = 'screenshots'
    os.makedirs(screenshots_dir, exist_ok=True)
    screenshot_path = os.path.join(screenshots_dir, f'{name}.png')
    driver.save_screenshot(screenshot_path)
    assert os.path.exists(screenshot_path), \
        f"Screenshot was not saved: {screenshot_path}"
    logging.info(f"Screenshot saved: {screenshot_path}")
