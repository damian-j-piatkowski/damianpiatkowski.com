"""Module for testing the resume functionality.

This module contains tests for viewing and downloading the resume,
ensuring that the resume page and download links work as expected.

Test Functions:
- test_navigate_to_resume: Tests navigation to the resume page.
- test_download_resume_pdf: Tests the PDF download functionality for the resume.
"""

import logging
import os
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from tests.e2e import utils


def test_navigate_to_resume(driver) -> None:
    """Test navigation to the resume page.

    This function clicks on the resume link and verifies that the resume page
    displays the correct heading.

    Args:
        driver: The WebDriver instance used to interact with the page.
    """
    driver.get(utils.get_base_url())

    try:
        resume_button_locator = (By.ID, 'view_resume_button')
        utils.retry_click(driver, resume_button_locator)
        resume_heading = WebDriverWait(driver, 20).until(
            ec.visibility_of_element_located((By.CLASS_NAME, 'resume-header')))
        assert 'Damian Piatkowski' in resume_heading.text
    except Exception as e:
        utils.capture_screenshot(driver, 'navigate_to_resume_exception')
        logging.error(f"Error navigating to resume: {e}")
        raise e


def test_download_resume_pdf(driver, clean_download_dir) -> None:
    """Test the resume PDF download functionality.

    This function clicks the download button on the resume page and waits
    for the PDF to be downloaded to the specified directory.

    Args:
        driver: The WebDriver instance used to interact with the page.
        clean_download_dir: The directory path where the resume PDF is expected
            to be downloaded.
    """
    resume_file = clean_download_dir
    crdownload_file = str(resume_file) + '.crdownload'
    driver.get(utils.get_base_url() + "/resume")

    try:
        download_button_locator = (By.ID, 'download_pdf_button')
        utils.retry_click(driver, download_button_locator)

        timeout = 120
        start_time = time.time()

        while not (
                os.path.exists(resume_file) or os.path.exists(crdownload_file)):
            if time.time() - start_time > timeout:
                utils.capture_screenshot(driver, 'download_resume_pdf_timeout')
                raise AssertionError("PDF download timed out")
            time.sleep(2)

        assert os.path.exists(resume_file) or os.path.exists(
            crdownload_file), "Resume PDF download failed."

    except Exception as e:
        logging.error(f"Error downloading resume PDF: {e}")
        raise e
