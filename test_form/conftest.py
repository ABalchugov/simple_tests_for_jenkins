import pytest
from selenium import webdriver
from utils import attach
from selenium.webdriver.chrome.options import Options


@pytest.fixture(scope="session", autouse=True)
def session_lifecycle():
    print("\n\n>>> [SESSION SETUP] Подключение к БД / Запуск сервера <<<")
    yield  # Здесь pytest прерывается и идет выполнять ВСЕ тесты сессии
    print("\n>>> [SESSION TEARDOWN] Отключение от БД / Остановка сервера <<<")


@pytest.fixture(scope="function", autouse=True)
def driver(request):
    print("\n\n>>> Открываем браузер <<<")
    # driver = webdriver.Chrome()
    # driver.maximize_window()

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

    print("\n\n>>> Закрываем браузер <<<")
    driver.quit()
