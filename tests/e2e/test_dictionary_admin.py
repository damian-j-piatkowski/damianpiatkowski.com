"""Selenium E2E coverage for dictionary admin authentication and workspace flows.

These tests expect a running application at BASE_URL (default http://localhost:5000)
and are selected with: pytest -m e2e
"""

import pytest
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from tests.e2e import selenium_utils as utils


def _skip_if_server_unavailable(driver):
    try:
        driver.get(utils.get_base_url())
    except WebDriverException as exc:
        pytest.skip(f"Application server unavailable for E2E: {exc}")


@pytest.mark.dictionary
@pytest.mark.e2e
def test_dictionary_page_loads(driver):
    """Public dictionary page is reachable and exposes the search field."""
    _skip_if_server_unavailable(driver)
    driver.get(f"{utils.get_base_url()}/dictionary")
    search = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.ID, "dictionary-search"))
    )
    assert search.is_displayed()


@pytest.mark.dictionary
@pytest.mark.e2e
def test_admin_login_page_loads(driver):
    """Admin login page is reachable through its direct URL."""
    _skip_if_server_unavailable(driver)
    driver.get(f"{utils.get_base_url()}/admin/login")
    assert WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.ID, "admin-login-form"))
    )


@pytest.mark.dictionary
@pytest.mark.e2e
def test_admin_create_workspace_requires_login(driver):
    """Unauthenticated visitors are redirected away from the create workspace."""
    _skip_if_server_unavailable(driver)
    driver.get(f"{utils.get_base_url()}/admin/dictionary/new")
    WebDriverWait(driver, 10).until(ec.url_contains("/admin/login"))
