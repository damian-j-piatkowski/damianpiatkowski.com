from selenium.common import ElementClickInterceptedException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


def test_contact_form_submission(driver):
    driver.get("http://localhost:5000")

    # Wait for the name input to be visible
    name_input = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.ID, 'name'))
    )
    email_input = driver.find_element(By.ID, 'email')
    message_input = driver.find_element(By.ID, 'message')
    submit_button = driver.find_element(By.ID, 'submit_button')

    # Fill out the form
    name_input.send_keys('John Doe')
    email_input.send_keys('john@example.com')
    message_input.send_keys('Hello, this is a test message.')

    # Scroll to the submit button and ensure it is in view
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_button)

    # Wait for the submit button to be clickable
    try:
        WebDriverWait(driver, 10).until(
            ec.element_to_be_clickable((By.ID, 'submit_button'))
        )
        submit_button.click()
    except ElementClickInterceptedException as e:
        print(f"Element click intercepted due to {e}, attempting to resolve...")

        # Retry scrolling and clicking
        driver.execute_script("window.scrollBy(0, -100);")  # Adjust scroll position
        WebDriverWait(driver, 10).until(
            ec.element_to_be_clickable((By.ID, 'submit_button'))
        )
        submit_button.click()
    except TimeoutException as e:
        print(f"Timeout waiting for element to be clickable: {e}")
        assert False, "Test failed due to timeout"

    # Wait for the flash message to appear
    flash_message = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.CLASS_NAME, 'flash-message'))
    )

    assert 'Message sent successfully!' in flash_message.text


def test_navigate_to_privacy_notice(driver):
    driver.get("http://localhost:5000")

    # Wait for the footer and the privacy link to be visible
    footer = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.TAG_NAME, 'footer'))
    )
    privacy_link = footer.find_element(By.LINK_TEXT, 'Privacy Notice')

    # Ensure the privacy link is in view
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", privacy_link)

    # Retry mechanism for clicking the privacy link
    attempt = 0
    while attempt < 3:
        try:
            privacy_link.click()
            break
        except ElementClickInterceptedException:
            attempt += 1
            driver.execute_script("window.scrollBy(0, -100);")  # Adjust scroll position
            if attempt == 3:
                raise

    # Wait for the privacy notice heading to be visible
    privacy_heading = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.CLASS_NAME, 'privacy-heading'))
    )

    assert 'Privacy Notice' in privacy_heading.text
