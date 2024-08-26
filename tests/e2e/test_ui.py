import logging
import os
import time

from selenium.common import ElementClickInterceptedException, TimeoutException, ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from tests.conftest import capture_screenshot

def retry_click(driver, by_locator, max_attempts=3, scroll_value=-300):
    """
    Retries clicking an element up to a specified maximum number of attempts, scrolling the window as needed.

    Args:
        driver: WebDriver instance from Selenium.
        by_locator: Tuple (By, str) representing the locator strategy and value (e.g., By.ID, 'view_resume_button').
        max_attempts (int, optional): Maximum number of attempts to click the element (default is 3).
        scroll_value (int, optional): Amount to scroll the window by when retrying clicks
                                     (positive for scrolling down, negative for scrolling up; default is -300).

    Raises:
        AssertionError: If the element is not clickable after the maximum number of attempts.

    Notes:
        - This function waits for the element identified by `by_locator` to be clickable using WebDriverWait.
        - If an ElementClickInterceptedException is raised during a click attempt, it scrolls the window by `scroll_value`.
        - If a TimeoutException occurs while waiting for the element to be clickable, a screenshot is captured and
          the test fails with an assertion error.
    """
    for attempt in range(max_attempts):
        try:
            element = WebDriverWait(driver, 20).until(
                ec.element_to_be_clickable(by_locator)
            )
            element.click()
            return
        except ElementClickInterceptedException:
            driver.execute_script(f"window.scrollBy(0, {scroll_value});")
        except TimeoutException:
            capture_screenshot(driver, 'retry_click_timeout')
            assert False, "Test failed due to timeout"
    capture_screenshot(driver, 'retry_click_error')
    raise AssertionError("Test failed due to element click intercepted after retries")



def test_contact_form_submission(driver):
    driver.get("http://web:5001")

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
    driver.get("http://web:5001")

    try:
        # Scroll down to bring the footer and privacy link into view
        driver.execute_script("window.scrollBy(0, 1500);")

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


def test_navigate_to_about_me(driver):
    driver.get("http://web:5001")

    try:
        # Check if the hamburger menu is present (for mobile view) and clickable
        try:
            hamburger_menu = WebDriverWait(driver, 5).until(
                ec.element_to_be_clickable((By.CLASS_NAME, 'navbar-toggler'))
            )
            logging.info("Hamburger menu detected, clicking it.")
            hamburger_menu.click()
        except (TimeoutException, ElementNotInteractableException):
            logging.info("Hamburger menu not interactable, likely in desktop view.")

        # Find and click the 'About' link in the navbar
        about_link = WebDriverWait(driver, 20).until(
            ec.visibility_of_element_located((By.ID, 'about_link'))
        )

        # Retry mechanism for clicking the about link
        attempt = 0
        while attempt < 3:
            try:
                WebDriverWait(driver, 20).until(
                    ec.element_to_be_clickable((By.ID, 'about_link'))
                )
                about_link.click()
                break
            except ElementClickInterceptedException:
                attempt += 1
                driver.execute_script("window.scrollBy(0, 300);")
                if attempt == 3:
                    capture_screenshot(driver, 'about_link_error')
                    raise
            except TimeoutException:
                capture_screenshot(driver, 'about_link_timeout')
                assert False, "Test failed due to timeout"

        # Wait for the 'About Me' section to be visible
        WebDriverWait(driver, 20).until(ec.visibility_of_element_located((By.ID, 'about')))

        # Check for the presence of some expected text in the About Me section
        about_content = driver.find_element(By.CLASS_NAME, 'about-content')
        assert 'Hello! I\'m a passionate back-end developer' in about_content.text
        assert 'Łódź, Poland' in about_content.text
        assert 'Breath of the Wild' in about_content.text
    except Exception as e:
        capture_screenshot(driver, 'test_navigate_to_about_me_exception')
        logging.error(f"Exception occurred: {e}")
        raise e


def test_navigate_back_to_index(driver):
    driver.get("http://web:5001/about-me")

    try:
        # Check if the hamburger menu is present (for mobile view) and clickable
        try:
            hamburger_menu = WebDriverWait(driver, 5).until(
                ec.element_to_be_clickable((By.CLASS_NAME, 'navbar-toggler'))
            )
            logging.info("Hamburger menu detected, clicking it.")
            hamburger_menu.click()
        except (TimeoutException, ElementNotInteractableException):
            logging.info("Hamburger menu not interactable, likely in desktop view.")

        # Find and click the 'Home' link in the navbar
        home_link = WebDriverWait(driver, 20).until(
            ec.visibility_of_element_located((By.ID, 'home_link'))
        )

        # Retry mechanism for clicking the home link
        attempt = 0
        while attempt < 3:
            try:
                WebDriverWait(driver, 20).until(
                    ec.element_to_be_clickable((By.ID, 'home_link'))
                )
                home_link.click()
                break
            except ElementClickInterceptedException:
                attempt += 1
                driver.execute_script("window.scrollBy(0, 300);")
                if attempt == 3:
                    capture_screenshot(driver, 'home_link_error')
                    raise
            except TimeoutException:
                capture_screenshot(driver, 'home_link_timeout')
                assert False, "Test failed due to timeout"

        # Wait for the 'Contact Me' section to be visible
        WebDriverWait(driver, 20).until(
            ec.visibility_of_element_located((By.CLASS_NAME, 'contact-section'))
        )

        # Check for the presence of some expected text in the Contact Me section
        contact_content = driver.find_element(By.CLASS_NAME, 'contact-text')
        assert 'Feel free to reach out to me directly' in contact_content.text
    except Exception as e:
        capture_screenshot(driver, 'test_navigate_back_to_index_exception')
        logging.error(f"Exception occurred: {e}")
        raise e


def test_navigate_to_resume(driver):
    driver.get("http://web:5001")

    try:
        # Wait for the resume link to be visible
        resume_button_locator = (By.ID, 'view_resume_button')
        WebDriverWait(driver, 20).until(
            ec.visibility_of_element_located(resume_button_locator)
        )

        # Retry clicking the resume button
        retry_click(driver, resume_button_locator, scroll_value=-300)

        # Wait for the resume section heading to be visible
        resume_heading = WebDriverWait(driver, 20).until(
            ec.visibility_of_element_located((By.CLASS_NAME, 'resume-header'))
        )
        assert 'Damian Piatkowski' in resume_heading.text
    except Exception as e:
        capture_screenshot(driver, 'test_navigate_to_resume_exception')
        logging.error(f"Exception occurred: {e}")
        raise


def test_download_resume_pdf(driver, clean_download_dir):
    resume_file = clean_download_dir
    driver.get("http://web:5001/resume")

    try:
        # Define locator and scroll value for retry_click
        download_button_locator = (By.ID, 'download_pdf_button')

        # Use retry_click for clicking the download button
        retry_click(driver, download_button_locator, scroll_value=-300)

        # Wait for the file to be downloaded
        timeout = 30  # seconds
        start_time = time.time()
        while not os.path.exists(resume_file):
            if time.time() - start_time > timeout:
                capture_screenshot(
                    driver, 'test_download_resume_pdf_timeout')
                assert False, "PDF was not downloaded within the timeout period"
            time.sleep(1)

        # Verify the file size is greater than 0
        assert os.path.getsize(resume_file) > 0, "Downloaded file is empty"

    except Exception as e:
        capture_screenshot(driver, 'test_download_resume_pdf_exception')
        logging.error(f"Exception occurred: {e}")
        raise e

