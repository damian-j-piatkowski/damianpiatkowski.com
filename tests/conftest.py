import os

import pytest
from selenium import webdriver
from pathlib import Path
import logging

from app import create_app


@pytest.fixture(scope='session')
def app():
    app = create_app()
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


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
        "download.default_directory": os.getenv('DOWNLOAD_DIRECTORY'),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument('--headless')  # Ensure tests can run without a UI
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    if 'user_agent' in request.param:
        options.add_argument(f"user-agent={request.param['user_agent']}")
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(request.param['width'], request.param['height'])
    yield driver
    driver.quit()


def capture_screenshot(driver, name):
    screenshots_dir = 'screenshots'
    os.makedirs(screenshots_dir, exist_ok=True)
    screenshot_path = os.path.join(screenshots_dir, f'{name}.png')
    driver.save_screenshot(screenshot_path)
    assert os.path.exists(screenshot_path), \
        f"Screenshot was not saved: {screenshot_path}"
    logging.info(f"Screenshot saved: {screenshot_path}")
