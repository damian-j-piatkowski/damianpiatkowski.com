"""Utilities for UI end-to-end tests.

Functions:
    capture_screenshot: Captures a screenshot of the browser window.
    get_base_url: Retrieves the base URL from environment variables.
    retry_click: Attempts to click a web element multiple times with optional
                 scrolling to bring the element into view if the click fails.

Example usage:
    capture_screenshot(driver, 'error_page')
    base_url = get_base_url()
    retry_click(driver, ('id', 'submit_button'))
"""

import logging
import os

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    TimeoutException
)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


def capture_screenshot(driver: WebDriver, name: str) -> None:
    """
    Capture a screenshot of the current browser window and save it to a file.

    Args:
        driver (selenium.webdriver.Chrome): The WebDriver instance used to
            interact with the browser.
        name (str): The name of the screenshot file (without extension).

    Raises:
        IOError: If the screenshot could not be saved.
        Exception: If an error occurs during the screenshot capture process.

    Example:
        capture_screenshot(driver, 'homepage_error')
    """
    try:
        screenshots_dir = 'screenshots'
        os.makedirs(screenshots_dir, exist_ok=True)
        screenshot_path = os.path.join(screenshots_dir, f'{name}.png')

        if driver.save_screenshot(screenshot_path):
            logging.info(
                f"Screenshot saved successfully at: "
                f"{os.path.abspath(screenshot_path)}")
        else:
            raise IOError(f"Failed to capture screenshot: {screenshot_path}")

    except Exception as e:
        logging.error(f"Error capturing screenshot: {e}")
        raise


def get_base_url() -> str:
    """
    Retrieves the base URL for the application.

    This function fetches the `BASE_URL` from the environment variables.
    If `BASE_URL` is not set, it defaults to 'http://localhost:5000'.

    Returns:
        str: The base URL for the application, either from the environment
        variable `BASE_URL` or the default value 'http://localhost:5000'.
    """
    return os.getenv('BASE_URL', 'http://localhost:5000')


def retry_click(
        driver: WebDriver,
        by_locator: WebElement | tuple[str, str],
        max_attempts: int = 5,
        scroll_value: int = 200
) -> None:
    """
    Attempts to click a web element multiple times, with optional scrolling
    to bring the element into view if the click fails.

    This function will retry the click action up to `max_attempts` times if
    the element is not clickable due to intercepting or interactability issues.
    It uses scrolling to adjust the view if needed.

    Args:
        driver (WebDriver): The Selenium WebDriver instance controlling the
            browser.
        by_locator (WebElement | tuple[str, str]): WebElement or locator tuple
            (e.g., ('id', 'element_id')) to find the element.
        max_attempts (int, optional): Maximum number of attempts to retry
            clicking. Defaults to 5.
        scroll_value (int, optional): Pixels to scroll between attempts.
            Defaults to 200.

    Raises:
        AssertionError: If the element is not clickable after the specified
            number of attempts.
        TimeoutException: If the element is not found or not clickable within
            the given time.
    """
    attempts = 0
    while attempts < max_attempts:
        try:
            # If by_locator is a tuple, convert it into a By locator
            if isinstance(by_locator, tuple):
                by, value = by_locator
                logging.info(
                    f"Attempting to click elem using locator: {by} = {value}")
                element = WebDriverWait(driver, 5).until(
                    ec.element_to_be_clickable((getattr(By, by.upper()), value))
                )
            else:
                element = by_locator
                logging.info(
                    "Attempting to click provided WebElement directly.")

            # Scroll to element center using ActionChains
            ActionChains(driver).move_to_element(element).perform()
            logging.info(
                f"Scrolling to elem before clicking. Attempt: {attempts + 1}")

            element.click()  # Attempt to click the element
            logging.info("Element clicked successfully.")
            return  # Click successful, exit function

        except (
                ElementClickInterceptedException,
                ElementNotInteractableException,
                TimeoutException) as e:
            attempts += 1
            logging.warning(
                f"Attempt {attempts} failed due to {type(e).__name__}; "
                f"retrying. Error: {e}. Locator: {by_locator}")

            # Scroll slightly and retry if attempts are left
            if attempts < max_attempts:
                driver.execute_script(f"window.scrollBy(0, {scroll_value});")
                logging.info(
                    f"Scrolled by {scroll_value} pixels and retrying click.")
            else:
                error_message = (f"Element {by_locator} not clickable after "
                                 f"{max_attempts} attempts.")
                logging.error(error_message)
                raise AssertionError(error_message) from e
