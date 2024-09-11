import logging
import os
import time

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from tests import utils


def test_contact_form_submission(driver):
    driver.get(utils.get_base_url())

    try:
        # Wait for the name input to be visible
        name_input = WebDriverWait(driver, 20).until(
            ec.visibility_of_element_located((By.ID, 'name')))
        email_input = driver.find_element(By.ID, 'email')
        message_input = driver.find_element(By.ID, 'message')
        submit_button = driver.find_element(By.ID, 'submit_button')

        # Fill out the form
        name_input.send_keys('John Doe')
        email_input.send_keys('john@example.com')
        message_input.send_keys('Hello, this is a test message.')

        # Ensure submit button is in view and interactable
        actions = ActionChains(driver)
        actions.move_to_element(submit_button).perform()

        # Ensure the button is visible and enabled
        assert submit_button.is_displayed() and submit_button.is_enabled(), "Submit button is not interactable"

        # Attempt to click the submit button
        submit_button.click()

        # Wait for the flash message to appear
        flash_message = WebDriverWait(driver, 20).until(
            ec.visibility_of_element_located((By.CLASS_NAME, 'flash-message')))
        assert 'Message sent successfully!' in flash_message.text
        logging.info("Form submission successful and flash message found.")

    except Exception as e:
        logging.error(f"Exception occurred during form submission: {e}")
        utils.capture_screenshot(driver, 'contact_form_submission_exception')
        raise e


def test_navigate_to_privacy_notice(driver):
    driver.get(utils.get_base_url())

    try:
        privacy_link_locator = (By.ID, 'privacy_notice_link')
        WebDriverWait(driver, 10).until(
            ec.presence_of_element_located(privacy_link_locator))
        utils.retry_click(driver, privacy_link_locator, max_attempts=5,
                          scroll_value=200)

        privacy_heading = WebDriverWait(driver, 20).until(
            ec.visibility_of_element_located(
                (By.CLASS_NAME, 'privacy-heading')))
        assert 'Privacy Notice' in privacy_heading.text

    except Exception as e:
        utils.capture_screenshot(driver,
                                 'test_navigate_to_privacy_notice_exception')
        logging.error(f"Exception occurred: {e}")
        raise e


def test_navigate_to_about_me(driver):
    driver.get(utils.get_base_url())

    try:
        about_link = WebDriverWait(driver, 20).until(
            ec.visibility_of_element_located((By.ID, 'about_link')))
        utils.retry_click(driver, (By.ID, 'about_link'), max_attempts=3,
                          scroll_value=300)

        about_content = WebDriverWait(driver, 20).until(
            ec.visibility_of_element_located((By.CLASS_NAME, 'about-content')))
        assert 'Hello! I\'m a passionate back-end developer' in about_content.text

    except Exception as e:
        utils.capture_screenshot(driver, 'test_navigate_to_about_me_exception')
        logging.error(f"Exception occurred: {e}")
        raise e


def test_navigate_back_to_index(driver):
    driver.get(utils.get_base_url() + "/about-me")

    try:
        home_link = WebDriverWait(driver, 20).until(
            ec.visibility_of_element_located((By.ID, 'home_link')))
        utils.retry_click(driver, (By.ID, 'home_link'), max_attempts=3,
                          scroll_value=300)

        contact_content = WebDriverWait(driver, 20).until(
            ec.visibility_of_element_located((By.CLASS_NAME, 'contact-text')))
        assert 'Feel free to reach out to me directly' in contact_content.text

    except Exception as e:
        utils.capture_screenshot(driver,
                                 'test_navigate_back_to_index_exception')
        logging.error(f"Exception occurred: {e}")
        raise e


def test_navigate_to_resume(driver):
    driver.get(utils.get_base_url())

    try:
        resume_button_locator = (By.ID, 'view_resume_button')
        WebDriverWait(driver, 20).until(
            ec.visibility_of_element_located(resume_button_locator))
        utils.retry_click(driver, resume_button_locator, scroll_value=-300)

        resume_heading = WebDriverWait(driver, 20).until(
            ec.visibility_of_element_located((By.CLASS_NAME, 'resume-header')))
        assert 'Damian Piatkowski' in resume_heading.text

    except Exception as e:
        utils.capture_screenshot(driver, 'test_navigate_to_resume_exception')
        logging.error(f"Exception occurred: {e}")
        raise


def test_download_resume_pdf(driver, clean_download_dir):
    resume_file = clean_download_dir
    crdownload_file = str(resume_file) + '.crdownload'
    driver.get(utils.get_base_url() + "/resume")

    download_button_locator = (By.ID, 'download_pdf_button')
    utils.retry_click(driver, download_button_locator, scroll_value=-300)

    timeout = 120
    start_time = time.time()

    while not (os.path.exists(resume_file) or os.path.exists(crdownload_file)):
        if time.time() - start_time > timeout:
            utils.capture_screenshot(driver, 'test_download_resume_pdf_timeout')
            assert False, "PDF was not downloaded within the timeout period"
        time.sleep(2)

    assert os.path.exists(resume_file) or os.path.exists(
        crdownload_file), "Neither resume.pdf nor resume.pdf.crdownload was found."
