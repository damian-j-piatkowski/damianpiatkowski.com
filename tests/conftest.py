import pytest
from selenium import webdriver

from app import create_app


@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True  # Ensure the app is in testing mode
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture(scope="module")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)  # Ensure chromedriver is installed and in PATH
    yield driver
    driver.quit()


