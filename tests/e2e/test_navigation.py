# """Module for testing navigation functionality.
#
# This module contains tests for navigating between different sections of the app,
# ensuring that users can access various pages and the correct content is
# displayed.
#
# Test Functions:
# - test_navigate_to_privacy_notice: Tests navigation to the privacy notice page.
# - test_navigate_to_about_me: Tests navigation to the About Me page.
# - test_navigate_back_to_index: Tests navigation back to the index (home) page.
# """
#
# import logging
#
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as ec
# from selenium.webdriver.support.ui import WebDriverWait
#
#
# def test_navigate_to_privacy_notice(driver) -> None:
#     """Test navigation to the privacy notice page.
#
#     This function clicks on the privacy notice link and verifies that the page
#     displays the correct content.
#
#     Args:
#         driver: The WebDriver instance used to interact with the page.
#     """
#     driver.get(utils.get_base_url())
#
#     try:
#         privacy_link_locator = (By.ID, 'privacy_notice_link')
#         utils.retry_click(driver, privacy_link_locator)
#         privacy_heading = WebDriverWait(driver, 20).until(
#             ec.visibility_of_element_located(
#                 (By.CLASS_NAME, 'privacy-heading')))
#         assert 'Privacy Notice' in privacy_heading.text
#     except Exception as e:
#         utils.capture_screenshot(driver, 'privacy_notice_exception')
#         logging.error(f"Error navigating to privacy notice: {e}")
#         raise e
#
#
# def test_navigate_to_about_me(driver) -> None:
#     """Test navigation to the About Me page.
#
#     This function clicks on the About Me link and verifies that the correct
#     content is displayed on the page.
#
#     Args:
#         driver: The WebDriver instance used to interact with the page.
#     """
#     driver.get(utils.get_base_url())
#
#     try:
#         # Expand the navbar if it is collapsed (for smaller screens)
#         utils.expand_navbar_if_collapsed(driver)
#
#         # Now click the About Me link
#         about_link_locator = (By.ID, 'about_link')
#         utils.retry_click(driver, about_link_locator)
#
#         # Verify the correct content is displayed
#         about_content = WebDriverWait(driver, 20).until(
#             ec.visibility_of_element_located((By.CLASS_NAME, 'about-content'))
#         )
#         assert (
#                 'Hello! I\'m a passionate back-end developer' in
#                 about_content.text)
#
#     except Exception as e:
#         utils.capture_screenshot(driver, 'about_me_exception')
#         logging.error(f"Error navigating to About Me: {e}")
#         raise e
#
#
# def test_navigate_back_to_index(driver) -> None:
#     """Test navigation back to the index (home) page.
#
#     This function navigates from the About Me page back to the home page,
#     verifying the presence of specific content.
#
#     Args:
#         driver: The WebDriver instance used to interact with the page.
#     """
#     driver.get(utils.get_base_url() + "/about-me")
#
#     try:
#         # Expand the navbar if it is collapsed (for smaller screens)
#         utils.expand_navbar_if_collapsed(driver)
#
#         # Now click the Home link
#         home_link_locator = (By.ID, 'home_link')
#         utils.retry_click(driver, home_link_locator)
#
#         # Verify the correct content is displayed on the Home page
#         contact_content = WebDriverWait(driver, 20).until(
#             ec.visibility_of_element_located((By.CLASS_NAME, 'contact-text'))
#         )
#         assert 'Feel free to reach out to me directly' in contact_content.text
#
#     except Exception as e:
#         utils.capture_screenshot(driver, 'navigate_back_to_index_exception')
#         logging.error(f"Error navigating back to index: {e}")
#         raise e
#
