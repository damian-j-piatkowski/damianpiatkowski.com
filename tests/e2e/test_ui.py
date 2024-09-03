import logging
import os
import time

from selenium.common.exceptions import ElementClickInterceptedException, \
    TimeoutException, ElementNotInteractableException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from tests.conftest import capture_screenshot


def is_element_fully_visible(driver, element):
    """Check if an element is fully within the viewport and not obscured."""
    element_rect = element.rect
    viewport_height = driver.execute_script("return window.innerHeight;")
    viewport_width = driver.execute_script("return window.innerWidth;")

    # Check if element is within viewport boundaries
    return (
            0 <= element_rect['x'] <= viewport_width - element_rect['width']
            and 0 <= element_rect['y'] <= viewport_height - element_rect[
                'height']
    )


def retry_click(driver, by_locator, max_attempts=5, scroll_value=200):
    """Retry click on an element with optional scrolling."""
    attempts = 0
    while attempts < max_attempts:
        try:
            # Wait until the element is clickable
            element = WebDriverWait(driver, 5).until(
                ec.element_to_be_clickable(by_locator))

            # Scroll to element center using ActionChains
            ActionChains(driver).move_to_element(element).perform()

            # Attempt to click the element
            element.click()
            return  # Click successful, exit function

        except (
        ElementClickInterceptedException, ElementNotInteractableException,
        TimeoutException) as e:
            attempts += 1
            logging.warning(f"Attempt {attempts} failed; retrying. Error: {e}")

            # Scroll slightly and retry if attempts are left
            if attempts < max_attempts:
                driver.execute_script(f"window.scrollBy(0, {scroll_value});")
            else:
                logging.error(
                    f"Element {by_locator} not clickable after {max_attempts} attempts.")
                raise AssertionError(
                    f"Element {by_locator} not clickable after {max_attempts} attempts.") from e


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

        # Wait for full page load
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script(
                'return document.readyState') == 'complete'
        )

        # Ensure submit button is in view and interactable
        actions = ActionChains(driver)
        actions.move_to_element(submit_button).perform()

        # Ensure the button is visible and enabled
        assert submit_button.is_displayed() and submit_button.is_enabled(), "Submit button is not interactable"

        # Attempt to click the submit button
        attempt = 0
        while attempt < 3:
            try:
                submit_button.click()
                break  # Exit loop if successful
            except ElementClickInterceptedException:
                attempt += 1
                logging.warning(
                    f"Attempt {attempt}: Click intercepted, retrying...")
                time.sleep(2)  # Add delay before retrying

                if attempt == 3:
                    capture_screenshot(driver,
                                       'contact_form_submission_failure')
                    raise
            except TimeoutException:
                capture_screenshot(driver, 'contact_form_submission_timeout')
                assert False, "Test failed due to timeout"

        # Wait for the flash message to appear
        flash_message = WebDriverWait(driver, 20).until(
            ec.visibility_of_element_located((By.CLASS_NAME, 'flash-message'))
        )

        assert 'Message sent successfully!' in flash_message.text
        logging.info("Form submission successful and flash message found.")

    except Exception as e:
        logging.error(f"Exception occurred during form submission: {e}")
        capture_screenshot(driver, 'contact_form_submission_exception')
        raise e


def test_navigate_to_privacy_notice(driver):
    driver.get("http://web:5001")

    try:
        # Wait for the privacy link to be present
        privacy_link_locator = (By.ID, 'privacy_notice_link')
        WebDriverWait(driver, 10).until(
            ec.presence_of_element_located(privacy_link_locator)
        )

        # Retry clicking the privacy link with a scroll adjustment
        retry_click(
            driver, privacy_link_locator, max_attempts=5, scroll_value=200)

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
            logging.info(
                "Hamburger menu not interactable, likely in desktop view.")

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
        WebDriverWait(driver, 20).until(
            ec.visibility_of_element_located((By.ID, 'about')))

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
            logging.info(
                "Hamburger menu not interactable, likely in desktop view.")

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


# def test_download_resume_pdf(driver, clean_download_dir):
#     resume_file = clean_download_dir
#     crdownload_file = str(resume_file) + '.crdownload'
#     driver.get("http://web:5001/resume")
#
#     try:
#         # Define locator and scroll value for retry_click
#         download_button_locator = (By.ID, 'download_pdf_button')
#
#         # Use retry_click for clicking the download button
#         retry_click(driver, download_button_locator, scroll_value=-300)
#
#         # Wait for the file to be downloaded
#         timeout = 120  # Increase timeout to 2 minutes
#         start_time = time.time()
#         last_size = 0
#
#         while os.path.exists(crdownload_file):
#             current_size = os.path.getsize(crdownload_file)
#             if current_size != last_size:
#                 last_size = current_size
#             else:
#                 if time.time() - start_time > timeout:
#                     capture_screenshot(driver,
#                                        'test_download_resume_pdf_timeout')
#                     assert False, "PDF was not downloaded within the timeout period"
#                 time.sleep(2)  # Wait 2 seconds before checking again
#
#         # Ensure the .crdownload is gone and the actual file exists
#         while not os.path.exists(resume_file):
#             if time.time() - start_time > timeout:
#                 capture_screenshot(driver, 'test_download_resume_pdf_timeout')
#                 assert False, "PDF was not downloaded within the timeout period"
#             time.sleep(1)
#
#         # Verify the file size is greater than 0
#         assert os.path.getsize(resume_file) > 0, "Downloaded file is empty"
#
#     except Exception as e:
#         capture_screenshot(driver, 'test_download_resume_pdf_exception')
#         logging.error(f"Exception occurred: {e}")
#         raise e
