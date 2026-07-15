import pytest
from selenium import webdriver
from utils import attach
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from dotenv import load_dotenv
import os

@pytest.fixture(scope="session", autouse=True)
def load_env():
    load_dotenv()

def pytest_addoption(parser):
    parser.addoption(
        "--browser",
        default="chrome",
        choices=("chrome", "firefox"),
        help="Browser to use"
    )
    parser.addoption(
        "--browser_version",
        default="150.0",
        choices=("152.0", "151.0", "150.0", "149.0", "148.0"),
        help="Browser version to use"
    )
    parser.addoption(
        "--headless",
        default=False,
        choices=(True, False),
        help="Browser version to use"
    )
    parser.addoption(
        "--window_size",
        default="1920*1080",
        help="Window size"
    )


@pytest.fixture(scope="function", autouse=True)
def driver(request):
    browser = request.config.getoption("--browser")
    browser_version = request.config.getoption("--browser_version")
    headless = request.config.getoption("--headless")
    window_size = request.config.getoption("--window_size")
    width_str, height_str = window_size.split("*", 1)

    width = int(width_str) if width_str else 1920
    height = int(height_str) if height_str else 1080

    options = None

    if browser == "chrome":
        options = ChromeOptions()
        options.add_argument(f"--window-size={width},{height}")
    elif browser == "firefox":
        options = FirefoxOptions()
        options.add_argument(f"--width={width}")
        options.add_argument(f"--height={height}")

    if headless:
        options.add_argument("--headless")

    selenoid_capabilities = {
        "browserName": browser,
        "browserVersion": browser_version,
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
