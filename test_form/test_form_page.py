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

    assert output is not None, "Блок с результатами не отобразился"
    assert output["name"] == name.strip()
    assert output["email"] == email.strip()
    assert output["current_address"] == current_address.strip()
    assert output["permanent_address"] == permanent_address.strip()
