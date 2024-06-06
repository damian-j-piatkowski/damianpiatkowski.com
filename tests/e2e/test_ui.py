import logging

from selenium.common import ElementClickInterceptedException, TimeoutException, ElementNotInteractableException
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


def test_navigate_to_about_me(driver):
    driver.get("http://localhost:5000")

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
        about_section = WebDriverWait(driver, 20).until(
            ec.visibility_of_element_located((By.ID, 'about'))
        )

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
    driver.get("http://localhost:5000/about-me")

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

        # Wait for the 'Contact Me' section to be visible (as an indication of being on the index page)
        contact_section = WebDriverWait(driver, 20).until(
            ec.visibility_of_element_located((By.CLASS_NAME, 'contact-section'))
        )

        # Check for the presence of some expected text in the Contact Me section
        contact_content = driver.find_element(By.CLASS_NAME, 'contact-text')
        assert 'Feel free to reach out to me directly' in contact_content.text
    except Exception as e:
        capture_screenshot(driver, 'test_navigate_back_to_index_exception')
        logging.error(f"Exception occurred: {e}")
        raise e
