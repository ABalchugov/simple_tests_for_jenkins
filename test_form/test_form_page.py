import time
import pytest
import allure
from selenium.webdriver.common.by import By

from test_form.form_page import FormPage

@allure.epic("UI Automation")
@allure.feature("Text Box Form")
@allure.story("Успешная отправка формы")
@allure.title("Отправка формы с корректными данными")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
@pytest.mark.regress
@pytest.mark.parametrize("name, email, current_address, permanent_address", [
    ("John Doe", "john@example.com", "123 Elm St", "456 Oak St"),  # Стандартный кейс
    ("Иван Иванов", "ivan@mail.ru", "ул. Ленина, д. 1", "ул. Пушкина, д. 2"),  # Кириллица
    ("A", "a@b.cc", "B", "C"),  # Минимальная длина строк
    ("Name-With Dash", "dash@email.co.uk", "Addr 1/2", "Addr 3 & 4"),  # Спецсимволы в полях
    ("   John   ", "spaces@test.com", "  Street 1  ", "  Street 2  "),  # Строки с пробелами
])
def test_positive_form_submission(driver, name, email, current_address, permanent_address):
    form_po = FormPage(driver)
    form_po.open()
    form_po.fill_form(name, email, current_address, permanent_address)
    form_po.click_submit_button()

    output = form_po.get_result_data()

    assert output is not None, "Блок с результатами не отобразился"
    assert output["name"] == name.strip()
    assert output["email"] == email.strip()
    assert output["current_address"] == current_address.strip()
    assert output["permanent_address"] == permanent_address.strip()

@allure.feature("Форма Text Box")
@allure.story("Частичное заполнение формы")
@allure.title("Отправка формы с заполненными не всеми полями")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regress
@pytest.mark.parametrize("name, email, current_address, permanent_address", [
    ("Only Name", "", "", ""),
    ("", "only@email.com", "", ""),
    ("", "", "Only Current Address", ""),
    ("", "", "", "Only Permanent Address"),
    ("Name & Email", "name_email@test.com", "", ""),
])
def test_partial_form_submission(driver, name, email, current_address, permanent_address):
    form_po = FormPage(driver)
    form_po.open()
    form_po.fill_form(name, email, current_address, permanent_address)
    form_po.click_submit_button()

    output = form_po.get_result_data()
    assert output is not None, "Форма должна отправляться при частичном заполнении"
    if name: assert output["name"] == name
    if email: assert output["email"] == email
    if current_address: assert output["current_address"] == current_address
    if permanent_address: assert output["permanent_address"] == permanent_address

@allure.feature("Валидация формы")
@allure.story("Проверка email")
@allure.title("Отображение ошибки при вводе некорректного email")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
@pytest.mark.regress
@pytest.mark.parametrize("invalid_email", [
    "plainaddress",  # Нет собаки и домена
    "@no-local-part.com",  # Нет имени пользователя
    pytest.param("john.doe@com", marks=pytest.mark.xfail(reason="Ожидаемая ошибка: нет доменной зоны верхнего уровня")),
    pytest.param("john@missing-dot", marks=pytest.mark.xfail(reason="Ожидаемая ошибка: нет точки в домене")),
    "john@@example.com",  # Две собаки
    "john@example..com",  # Две точки подряд
])
def test_invalid_email_validation(driver, invalid_email):
    form_po = FormPage(driver)
    form_po.open()
    form_po.fill_form("Test", invalid_email)
    form_po.click_submit_button()

    # Ожидаем, что блок вывода не появился ИЛИ поле подсвечено ошибкой
    output = form_po.get_result_data()

    time.sleep(1)
    assert output is None or form_po.is_email_error_present(), f"Email '{invalid_email}' не должен быть принят системой"

@allure.feature("Граничные значения")
@allure.story("Проверка длинных строк")
@allure.title("Отправка формы с максимально длинными значениями")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regress
@pytest.mark.parametrize("field_type, long_string", [
    ("name", "A" * 1000),  # Экстремально длинное имя
    ("email", f"{'b' * 64}@example.com"),  # Максимальная длина локальной части email
    ("current_address", "Current " * 200),  # Длинный адрес (проверка на переполнение)
    ("permanent_address", "Permanent " * 200)  # Длинный адрес
])
def test_long_input_fields(driver, field_type, long_string):
    form_po = FormPage(driver)
    form_po.open()

    form_po.fill_form(**{field_type: long_string})

    form_po.click_submit_button()
    output = form_po.get_result_data()
    assert output is not None, f"Форма не справилась с длинной строкой в поле {field_type}"

@allure.feature("Безопасность")
@allure.story("Защита от XSS и HTML-инъекций")
@allure.title("Обработка потенциально опасного ввода")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.regress
@pytest.mark.parametrize("security_payload", [
    "<script>alert('xss')</script>",  # Базовый XSS скрипт
    "1' OR '1'='1",  # Базовая SQL-инъекция
    ":):):):))))::;)",  # Суррогатные пары (Эмодзи)
    "<div>HTML injection</div>"  # Теги верстки
])
def test_security_and_special_inputs(driver, security_payload):
    form_po = FormPage(driver)
    form_po.open()

    form_po.fill_form(name=security_payload, current_address=security_payload, permanent_address=security_payload)
    form_po.click_submit_button()

    output = form_po.get_result_data()
    assert output is not None, "Форма упала при вводе спецсимволов/инъекций"
    # Текст должен отобразиться строго как строка, а не выполниться кодом
    assert output["name"] == security_payload
    assert output["current_address"] == security_payload
    assert output["permanent_address"] == security_payload

    assert len(driver.find_elements(By.CSS_SELECTOR, "#output script")) == 0

    output_html = form_po.result_box_name_locator.get_attribute("innerHTML")

    assert "<script>" not in output_html.lower()

@allure.feature("Форма Text Box")
@allure.story("Отправка пустой формы")
@allure.title("Отправка формы без заполнения полей")
@allure.severity(allure.severity_level.MINOR)
@pytest.mark.smoke
@pytest.mark.regress
def test_empty_form_submission(driver):
    form_po = FormPage(driver)
    form_po.open()
    form_po.click_submit_button()
    time.sleep(5)

    output = form_po.get_result_data()
    if output is not None:
        assert output["name"] == ""
        assert output["email"] == ""
        assert output["current_address"] == ""
        assert output["permanent_address"] == ""
