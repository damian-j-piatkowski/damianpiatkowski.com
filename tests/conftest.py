import os
from pathlib import Path

import pytest
from selenium import webdriver
from sqlalchemy.orm import sessionmaker, scoped_session

from app import create_app, db
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
    # Establish a connection and begin a transaction
    connection = _db.engine.connect()
    transaction = connection.begin()

    # Create a session factory bound to the current connection
    session_factory = sessionmaker(bind=connection)
    # Use scoped_session to manage the session's state
    test_session = scoped_session(session_factory)

    # Assign the test session to the _db's session attribute
    _db.session = test_session

    try:
        # Provide the session to the test
        yield test_session
    except Exception as e:
        # Catch exceptions to ensure cleanup
        print(f"Error during test session: {e}")
        raise
    finally:
        # Ensure rollback and cleanup are executed regardless of test outcome
        try:
            transaction.rollback()
        except Exception as rollback_error:
            print(f"Error during rollback: {rollback_error}")
        finally:
            # Close the connection and remove the session
            connection.close()
            test_session.remove()


@pytest.fixture
def clean_download_dir():
    download_directory = os.getenv("DOWNLOAD_DIRECTORY")
    resume_file = Path(download_directory) / "resume.pdf"
    crdownload_file = Path(download_directory) / "resume.pdf.crdownload"

    # Setup: Ensure both the .pdf and .crdownload files are cleaned before
    for file in [resume_file, crdownload_file]:
        if file.exists():
            file.unlink()

    yield resume_file

    # Teardown: Ensure both files are cleaned up after the test
    for file in [resume_file, crdownload_file]:
        if file.exists():
            file.unlink()


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
        "profile.default_content_settings.popups": 0,
        "safebrowsing.disable_download_protection": True
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
