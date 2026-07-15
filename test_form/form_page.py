from seleniumpagefactory.Pagefactory import PageFactory
from seleniumpagefactory.Pagefactory import ElementNotVisibleException
import os


class FormPage(PageFactory):

    def __init__(self, driver):
        self.driver = driver
        self.url = os.getenv("TEST_URL")
        self.locators = {
            "full_name_locator": ('ID', "userName"),
            "email_locator": ('ID', "userEmail"),
            "current_address_locator": ('ID', "currentAddress"),
            "permanent_address_locator": ('ID', "permanentAddress"),
            "submit_button_locator": ('ID', "submit"),
            "result_box_locator": ('ID', "output"),
            "result_box_name_locator": ('ID', "name"),
            "result_box_email_locator": ('ID', "email"),
            "result_box_current_address_locator": ('CSS', '#output #currentAddress'),
            "result_box_permanent_address_locator": ('CSS', '#output #permanentAddress')
        }

    def open(self):
        self.driver.get(self.url)

    def fill_full_name_field(self, name):
        self.full_name_locator.set_text(name)

    def fill_email_field(self, email):
        self.email_locator.send_keys(email)

    def fill_current_address_field(self, current_address):
        self.current_address_locator.send_keys(current_address)

    def fill_permanent_address_field(self, permanent_address):
        self.permanent_address_locator.send_keys(permanent_address)

    def click_submit_button(self):
        self.submit_button_locator.click()

    def fill_form(self, name="", email="", current_address="", permanent_address=""):
        if name != "":
            self.fill_full_name_field(name)
        if email != "":
            self.fill_email_field(email)
        if current_address != "":
            self.fill_current_address_field(current_address)
        if permanent_address != "":
            self.fill_permanent_address_field(permanent_address)

    def get_result_data(self):
        try:
            if not self.result_box_locator.is_displayed():
                return None
        except ElementNotVisibleException:
            return None

        name = self.result_box_name_locator.text.replace("Name:", "").strip()
        email = self.result_box_email_locator.text.replace("Email:", "").strip()
        current_address = self.result_box_current_address_locator.text.replace("Current Address :", "").strip()
        permanent_address = self.result_box_permanent_address_locator.text.replace("Permananet Address :", "").strip()

        return {"name": name, "email": email, "current_address": current_address,
                "permanent_address": permanent_address}

    def is_email_error_present(self):
        return not self.driver.execute_script(
            "return arguments[0].checkValidity();",
            self.email_locator
        )
