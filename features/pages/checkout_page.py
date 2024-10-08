from .base_page import BasePage
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

class CheckoutPage(BasePage):
    """
    Page object for the checkout page, containing specific elements and methods.
    """

    URL = "https://aeonstest.info/checkout/"

    def __init__(self, browser):
        """
        Initialize the CheckoutPage with a browser instance.
        
        :param browser: Selenium WebDriver instance
        """
        super().__init__(browser)

    @property
    def checkout_header(self):
        return self.browser.find_element(By.CSS_SELECTOR, "h1.checkout-title")

    @property
    def email_input(self):
        return self.browser.find_element(By.ID, "app_one_page_checkout_customer_email")

    @property
    def first_name_input(self):
        return self.browser.find_element(By.ID, "app_one_page_checkout_billingAddress_firstName")

    @property
    def last_name_input(self):
        return self.browser.find_element(By.ID, "app_one_page_checkout_billingAddress_lastName")

    @property
    def phone_input(self):
        return self.browser.find_element(By.ID, "app_one_page_checkout_billingAddress_phoneNumber")

    @property
    def address_input(self):
        return self.browser.find_element(By.ID, "app_one_page_checkout_billingAddress_street")

    @property
    def city_input(self):
        return self.browser.find_element(By.ID, "app_one_page_checkout_billingAddress_city")

    @property
    def postcode_input(self):
        return self.browser.find_element(By.ID, "app_one_page_checkout_billingAddress_postcode")

    @property
    def country_selector(self):
        return self.browser.find_element(By.ID, "app_one_page_checkout_billingAddress_countryCode")

    def is_url_matches(self):
        """
        Check if the current URL matches the checkout page URL.
        
        :return: True if URLs match, False otherwise
        """
        return self.get_current_url() == self.URL

    def is_checkout_page(self):
        """
        Verify that the current page is the checkout page by checking the presence of the checkout header.
        
        :return: True if on the checkout page, False otherwise
        """
        return self.is_element_visible((By.CSS_SELECTOR, "h1.checkout-title"))

    def fill_in_checkout_form(self, email, first_name, last_name, phone, address, city, postcode, country):
        """
        Fill in the checkout form with the provided information.
        
        :param email: string, customer's email address
        :param first_name: string, customer's first name
        :param last_name: string, customer's last name
        :param phone: string, customer's phone number
        :param address: string, customer's street address
        :param city: string, customer's city
        :param postcode: string, customer's postal code
        :param country: string, customer's country (must match an option in the dropdown)
        """
        self.enter_text((By.ID, "app_one_page_checkout_customer_email"), email)
        self.enter_text((By.ID, "app_one_page_checkout_billingAddress_firstName"), first_name)
        self.enter_text((By.ID, "app_one_page_checkout_billingAddress_lastName"), last_name)
        self.enter_text((By.ID, "app_one_page_checkout_billingAddress_phoneNumber"), phone)
        self.enter_text((By.ID, "app_one_page_checkout_billingAddress_street"), address)
        self.enter_text((By.ID, "app_one_page_checkout_billingAddress_city"), city)
        self.enter_text((By.ID, "app_one_page_checkout_billingAddress_postcode"), postcode)
        self.select_dropdown_option((By.ID, "app_one_page_checkout_billingAddress_countryCode"), country)