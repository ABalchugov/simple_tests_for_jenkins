import pytest
from selenium import webdriver
from utils import attach
from selenium.webdriver.chrome.options import Options


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
    driver = webdriver.Remote(
        command_executor=f"https://user1:1234@selenoid.autotests.cloud/wd/hub",
        options=options
    )

    yield driver

    attach.add_html(driver)
    attach.add_screenshot(driver)
    attach.add_logs(driver)
    attach.add_video(driver)

    driver.quit()
