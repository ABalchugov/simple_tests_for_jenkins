import pytest
from selenium import webdriver
from utils import attach
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
import os

@pytest.fixture(scope="session", autouse=True)
def load_env():
    load_dotenv()

@pytest.fixture(scope="function", autouse=True)
def driver(request):
    options = Options()
    selenoid_capabilities = {
        "browserName": "chrome",
        "browserVersion": "148.0",
        "selenoid:options": {
            "enableVNC": True,
            "enableVideo": True
        }
    }
    options.capabilities.update(selenoid_capabilities)
    selenoid_login = os.getenv("SELENOID_LOGIN")
    selenoid_pass = os.getenv("SELENOID_PASS")
    selenoid_url = os.getenv("SELENOID_URL")
    driver = webdriver.Remote(
        command_executor=f"https://{selenoid_login}:{selenoid_pass}@{selenoid_url}/wd/hub",
        options=options
    )

    yield driver

    attach.add_html(driver)
    attach.add_screenshot(driver)
    attach.add_logs(driver)
    attach.add_video(driver)

    driver.quit()
