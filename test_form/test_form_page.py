import pytest
import allure
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
])
def test_positive_form_submission(driver, name, email, current_address, permanent_address):
    form_po = FormPage(driver)
    form_po.open()
    form_po.fill_form(name, email, current_address, permanent_address)
    form_po.click_submit_button()

    output = form_po.get_result_data()
    with allure.step("Проверить отображение блока результатов"):
        assert output is not None, "Блок с результатами не отобразился"
    with allure.step("Проверить введенные данные"):
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
    ("", "", "", "Only Permanent Address")
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

    assert output is None or form_po.is_email_error_present(), f"Email '{invalid_email}' не должен быть принят системой"


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

    output = form_po.get_result_data()
    if output is not None:
        assert output["name"] == ""
        assert output["email"] == ""
        assert output["current_address"] == ""
        assert output["permanent_address"] == ""
