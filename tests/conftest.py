import os

import pytest
from selenium import webdriver
import logging

from app import create_app


@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True  # Ensure the app is in testing mode
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


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
    options.add_argument('--headless')  # Ensure tests can run without a UI
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    if 'user_agent' in request.param:
        options.add_argument(f"user-agent={request.param['user_agent']}")
    driver = webdriver.Chrome(options=options)  # Ensure chromedriver is installed and in PATH
    driver.set_window_size(request.param['width'], request.param['height'])
    yield driver
    driver.quit()


def capture_screenshot(driver, name):
    screenshots_dir = 'screenshots'
    os.makedirs(screenshots_dir, exist_ok=True)
    screenshot_path = os.path.join(screenshots_dir, f'{name}.png')
    driver.save_screenshot(screenshot_path)
    assert os.path.exists(screenshot_path), f"Screenshot was not saved: {screenshot_path}"
    logging.info(f"Screenshot saved: {screenshot_path}")
