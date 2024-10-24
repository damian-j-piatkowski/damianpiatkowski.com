"""Module for testing the contact form functionality.

This module contains tests for the contact form submission process, ensuring
that the form behaves as expected and provides proper feedback on success or
failure.

Test Functions:
- test_contact_form_submission: Tests the contact form submission process,
    verifying form field interaction and flash message on successful submission.
"""

import logging

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from tests.e2e import utils


def test_contact_form_submission(driver) -> None:
    """Test the contact form submission functionality.

    This function interacts with the contact form on the page, filling in the
    required fields and verifying that the form submits successfully. It also
    checks for the presence of a flash message indicating success.

    Args:
        driver: The WebDriver instance used to interact with the page.
    """
    driver.get(utils.get_base_url())
    # Scroll to the bottom of the home page
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    try:
        # Wait for the form to be visible and scroll to it
        form_section = WebDriverWait(driver, 20).until(
            ec.visibility_of_element_located((By.ID, 'submit_button'))
            # Replace with the actual ID or locator of the form section
        )

        # Scroll to the form section using ActionChains
        actions = ActionChains(driver)
        actions.move_to_element(form_section).perform()

        name_input = WebDriverWait(driver, 20).until(
            ec.visibility_of_element_located((By.ID, 'name')))
        email_input = driver.find_element(By.ID, 'email')
        message_input = driver.find_element(By.ID, 'message')
        submit_button = driver.find_element(By.ID, 'submit_button')

        name_input.send_keys('John Doe')
        email_input.send_keys('john@example.com')
        message_input.send_keys('Hello, this is a test message.')

        submit_button.click()

        flash_message = WebDriverWait(driver, 20).until(
            ec.visibility_of_element_located((By.CLASS_NAME, 'flash-message')))
        assert 'Message sent successfully!' in flash_message.text
        logging.info("Form submission successful.")

    except Exception as e:
        logging.error(f"Error during form submission: {e}")
        utils.capture_screenshot(driver, 'contact_form_submission_exception')
        raise e
