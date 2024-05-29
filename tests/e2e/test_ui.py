import logging

from selenium.common import ElementClickInterceptedException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from tests.conftest import capture_screenshot


def test_contact_form_submission(driver):
    driver.get("http://localhost:5000")

    try:
        # Wait for the name input to be visible
        name_input = WebDriverWait(driver, 20).until(
            ec.visibility_of_element_located((By.ID, 'name'))
        )
        email_input = driver.find_element(By.ID, 'email')
        message_input = driver.find_element(By.ID, 'message')
        submit_button = driver.find_element(By.ID, 'submit_button')

        # Fill out the form
        name_input.send_keys('John Doe')
        email_input.send_keys('john@example.com')
        message_input.send_keys('Hello, this is a test message.')

        # Scroll down to ensure the submit button is in view
        driver.execute_script("window.scrollBy(0, 1300);")

        # Attempt to click the submit button
        attempt = 0
        while attempt < 3:
            try:
                WebDriverWait(driver, 20).until(
                    ec.element_to_be_clickable((By.ID, 'submit_button'))
                )
                submit_button.click()
                break
            except ElementClickInterceptedException:
                attempt += 1
                driver.execute_script("window.scrollBy(0, 500);")
                if attempt == 3:
                    capture_screenshot(driver, 'contact_form_submission_failure')
                    raise
            except TimeoutException:
                capture_screenshot(driver, 'contact_form_submission_timeout')
                assert False, "Test failed due to timeout"

        # Wait for the flash message to appear
        flash_message = WebDriverWait(driver, 20).until(
            ec.visibility_of_element_located((By.CLASS_NAME, 'flash-message'))
        )

        assert 'Message sent successfully!' in flash_message.text
    except Exception as e:
        capture_screenshot(driver, 'contact_form_submission_exception')
        raise e


def test_navigate_to_privacy_notice(driver):
    driver.get("http://localhost:5000")

    try:
        # Scroll down to bring the footer and privacy link into view
        driver.execute_script("window.scrollBy(0, 1300);")

        # Wait for the privacy link to be visible and clickable
        privacy_link = WebDriverWait(driver, 20).until(
            ec.visibility_of_element_located((By.ID, 'privacy_notice_link'))
        )

        # Retry mechanism for clicking the privacy link
        attempt = 0
        while attempt < 3:
            try:
                WebDriverWait(driver, 20).until(
                    ec.element_to_be_clickable((By.ID, 'privacy_notice_link'))
                )
                privacy_link.click()
                break
            except ElementClickInterceptedException:
                attempt += 1
                driver.execute_script("window.scrollBy(0, 300);")
                if attempt == 3:
                    capture_screenshot(driver, 'privacy_notice_error')
                    raise
            except TimeoutException:
                capture_screenshot(driver, 'privacy_notice_timeout')
                assert False, "Test failed due to timeout"

        # Wait for the privacy notice heading to be visible
        privacy_heading = WebDriverWait(driver, 20).until(
            ec.visibility_of_element_located((By.CLASS_NAME, 'privacy-heading'))
        )

        assert 'Privacy Notice' in privacy_heading.text
    except Exception as e:
        capture_screenshot(driver, 'test_navigate_to_privacy_notice_exception')
        logging.error(f"Exception occurred: {e}")
        raise e

