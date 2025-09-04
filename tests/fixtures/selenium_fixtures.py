"""Selenium-related pytest fixtures for setting up and managing the web driver.

This module includes fixtures for initializing a Selenium web driver with
different screen sizes and settings, and it handles the setup and teardown
of the browser for each test session.

Fixtures:
    - driver: Provides a Selenium web driver instance configured for various
      screen sizes and user agents, including mobile and desktop setups.
"""

import os
from typing import Optional

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver


@pytest.fixture(scope='module', params=[
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
def driver(request: pytest.FixtureRequest) -> Optional[WebDriver]:
    """Provides a Selenium web driver instance.

    Configures it with the specified screen size and optional user agent.

    Args:
        request (FixtureRequest): The pytest request object used to
            access fixture parameters.

    Yields:
        WebDriver: A Selenium WebDriver instance configured with the given
            settings.
    """
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
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # Cast request to include param to avoid type checking errors
    params = getattr(request, 'param', {})

    # Add custom user-agent if defined in request parameters
    if 'user_agent' in params:
        options.add_argument(f"user-agent={params['user_agent']}")

    driver: Optional[WebDriver] = None  # Initialize driver variable
    try:
        driver = webdriver.Chrome(options=options)
        driver.set_window_size(params['width'], params['height'])
        yield driver
    finally:
        if driver is not None:
            driver.quit()
