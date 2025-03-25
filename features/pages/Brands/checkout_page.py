from features.pages.Common.base_page import BasePage
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import re
import logging

logger = logging.getLogger(__name__)

class CheckoutPage(BasePage):
    """
    Page object for the checkout page, containing specific elements and methods.
    """

    SELECTORS = {
        'PAYPAL_OPTION': (By.ID, 'paypal-payment-option'),
        'PAYPAL_BUTTON': (By.ID, 'paypal-button'),
        'PAYPAL_RADIO': (By.CSS_SELECTOR, 'input[name="app_one_page_checkout[payments][0][method]"][value="paypal"]'),
        'PAYPAL_LABEL': (By.CSS_SELECTOR, 'label:has(input[name="app_one_page_checkout[payments][0][method]"][value="paypal"])'),
        'PAYMENT_COMPONENT': (By.CSS_SELECTOR, '.payment-component'),
        'COMPLETE_PURCHASE_BUTTON': (By.CSS_SELECTOR, 'button[type="submit"][form="app_one_page_checkout"]'),
        'PAYMENT_SUCCESS': (By.CSS_SELECTOR, '.payment-success-message'),
        # Billing Form Fields
        'EMAIL': (By.ID, 'app_one_page_checkout_customer_email'),
        'FIRST_NAME': (By.ID, 'app_one_page_checkout_billingAddress_firstName'),
        'LAST_NAME': (By.ID, 'app_one_page_checkout_billingAddress_lastName'),
        'PHONE': (By.ID, 'app_one_page_checkout_billingAddress_phoneNumber'),
        'ADDRESS': (By.ID, 'app_one_page_checkout_billingAddress_street'),
        'CITY': (By.ID, 'app_one_page_checkout_billingAddress_city'),
        'POSTCODE': (By.ID, 'app_one_page_checkout_billingAddress_postcode'),
        'COUNTRY': (By.ID, 'app_one_page_checkout_billingAddress_countryCode'),
        # Checkout Form
        'SAME_ADDRESS_CHECKBOX': (By.ID, 'app_one_page_checkout_differentShippingAddress_0'),
        'DIFFERENT_ADDRESS_CHECKBOX': (By.ID, 'app_one_page_checkout_differentShippingAddress_1'),
        # Shipping Form Fields
        'SHIPPING_FIRST_NAME': (By.ID, 'app_one_page_checkout_shippingAddress_firstName'),
        'SHIPPING_LAST_NAME': (By.ID, 'app_one_page_checkout_shippingAddress_lastName'),
        'SHIPPING_PHONE': (By.ID, 'app_one_page_checkout_shippingAddress_phoneNumber'),
        'SHIPPING_ADDRESS': (By.ID, 'app_one_page_checkout_shippingAddress_street'),
        'SHIPPING_CITY': (By.ID, 'app_one_page_checkout_shippingAddress_city'),
        'SHIPPING_POSTCODE': (By.ID, 'app_one_page_checkout_shippingAddress_postcode'),
        'SHIPPING_COUNTRY': (By.ID, 'app_one_page_checkout_shippingAddress_countryCode'),
        # Stripe Card Fields
        'CARD_NUMBER': (By.CSS_SELECTOR, 'input[data-elements-stable-field-name="cardNumber"]'),
        'CARD_EXPIRY': (By.CSS_SELECTOR, 'input[data-elements-stable-field-name="cardExpiry"]'),
        'CARD_CVC': (By.CSS_SELECTOR, 'input[data-elements-stable-field-name="cardCvc"]'),
        # Order Summary
        'SHIPPING_COST': (By.CSS_SELECTOR, '.order-summary-component .ch-shipping-value span'),
        'ORDER_TOTAL': (By.CSS_SELECTOR, '.order-summary-component .ch-total-value span'),
        # Submit Button
        'SUBMIT_BUTTON': (By.CSS_SELECTOR, 'button[type="submit"]'),
        # Page Elements
        'CHECKOUT_TITLE': (By.XPATH, '//*[@class="checkout-title"]'),
        'CHECKOUT_FORM': (By.CSS_SELECTOR, 'form[name="app_one_page_checkout"]'),
        'APP_CHECKOUT': (By.XPATH, '//*[@id="app_one_page_checkout"]//h2'),
        'PROCESSING_ICON': (By.XPATH, '//*[@class="PROCESSING_ICON_SELECTOR"]'),
        # Shipping Methods
        'SHIPPING_METHODS_LIST': (By.ID, 'app-checkout-shipping-methods'),
        'SELECTED_SHIPPING_METHOD': (By.XPATH, "//ul[@id='app-checkout-shipping-methods']//input[@type='radio' and @checked]/../span[@class='ch-custom-label']/span"),
        'ERROR_MESSAGE': (By.CSS_SELECTOR, '.alert.alert-danger'),
        'ABANDON_CHECKOUT_BUTTON': (By.CSS_SELECTOR, '.abandon-checkout-btn')
    }

    def __init__(self, browser):
        super().__init__(browser)
        self.url = '/checkout'

    def wait_for_page_load(self, timeout: int = 10) -> None:
        """Wait for the checkout page to load completely."""
        WebDriverWait(self.browser, timeout).until(
            EC.presence_of_element_located(self.SELECTORS['CHECKOUT_TITLE'])
        )

    def fill_in_checkout_form(self, user_data: dict) -> None:
        """
        Fill in the checkout form with provided user data.

        :param user_data: Dictionary containing user information
        """
        required_fields = ['email', 'first_name', 'last_name', 'phone', 'address', 'city', 'postcode', 'country']
        for field in required_fields:
            if field not in user_data:
                raise ValueError(f"Missing required field: {field}")

        field_mapping = {
            'email': self.SELECTORS['EMAIL'],
            'first_name': self.SELECTORS['FIRST_NAME'],
            'last_name': self.SELECTORS['LAST_NAME'],
            'phone': self.SELECTORS['PHONE'],
            'address': self.SELECTORS['ADDRESS'],
            'city': self.SELECTORS['CITY'],
            'postcode': self.SELECTORS['POSTCODE'],
            'country': self.SELECTORS['COUNTRY']
        }

        # Wait for form to be ready
        self.wait_for_checkout_form()

        # Fill in each field
        for data_key, selector in field_mapping.items():
            element = self.browser.find_element(*selector)
            element.clear()
            element.send_keys(user_data[data_key])

            if data_key == 'country':
                self.wait_for_ajax()
                self.select_dropdown_option(selector, user_data['country'])

    def wait_for_checkout_form(self, timeout: int = 10) -> None:
        """Wait for the checkout form to be visible."""
        WebDriverWait(self.browser, timeout).until(
            EC.visibility_of_element_located(self.SELECTORS['EMAIL'])
        )

    def use_same_address_for_billing_and_shipping(self) -> None:
        """Ensure that the same address is used for both billing and shipping."""
        checkbox = self.browser.find_element(*self.SELECTORS['SAME_ADDRESS_CHECKBOX'])
        if not checkbox.is_selected():
            checkbox.click()

    def enter_payment_details(self, payment_details: dict) -> None:
        """
        Enter payment details into Stripe iframe fields.

        :param payment_details: Dictionary containing card details
        """
        # Card Number Frame
        self.switch_to_stripe_frame('Secure card number input frame')
        card_number = self.browser.find_element(*self.SELECTORS['CARD_NUMBER'])
        card_number.send_keys(payment_details['cardNumber'])
        self.browser.switch_to.default_content()

        # Card Expiry Frame
        self.switch_to_stripe_frame('Secure expiration date input frame')
        card_expiry = self.browser.find_element(*self.SELECTORS['CARD_EXPIRY'])
        card_expiry.send_keys(payment_details['cardExpiry'])
        self.browser.switch_to.default_content()

        # Card CVC Frame
        self.switch_to_stripe_frame('Secure CVC input frame')
        card_cvc = self.browser.find_element(*self.SELECTORS['CARD_CVC'])
        card_cvc.send_keys(payment_details['cardCvc'])
        self.browser.switch_to.default_content()

    def select_shipping_method(self, method: str) -> None:
        """
        Select a shipping method.

        :param method: The shipping method to select
        """
        xpath = f"//span[contains(text(), '{method}')]/../../input[@type='radio']"
        try:
            element = self.browser.find_element(By.XPATH, xpath)
            element.click()
        except NoSuchElementException:
            raise Exception(f"Shipping method not found: {method}")

    def get_selected_shipping_method(self) -> str:
        """Get the selected shipping method."""
        try:
            element = self.browser.find_element(*self.SELECTORS['SELECTED_SHIPPING_METHOD'])
            return element.text.strip()
        except NoSuchElementException:
            logger.error("No shipping method element found")
            return None

    def get_shipping_cost(self) -> str:
        """Get the displayed shipping cost."""
        element = self.browser.find_element(*self.SELECTORS['SHIPPING_COST'])
        return element.text

    def get_order_total(self) -> float:
        """Get the order total amount."""
        element = self.browser.find_element(*self.SELECTORS['ORDER_TOTAL'])
        return self._parse_price(element.text)

    def complete_purchase(self) -> None:
        """Complete the purchase by clicking the submit button."""
        button = self.browser.find_element(*self.SELECTORS['SUBMIT_BUTTON'])
        button.click()

    def is_checkout_page(self) -> bool:
        """Verify that the current page is the checkout page."""
        return (self.is_element_visible(self.SELECTORS['CHECKOUT_TITLE']) and
                self.is_element_present(self.SELECTORS['CHECKOUT_FORM']))

    def get_page_title(self) -> str:
        """Get the page title text."""
        element = self.browser.find_element(*self.SELECTORS['APP_CHECKOUT'])
        return element.text

    def is_processing_page_displayed(self) -> bool:
        """Check if the processing page is displayed."""
        return self.is_element_visible(self.SELECTORS['PROCESSING_ICON'])

    def choose_paypal_payment(self) -> None:
        """Select PayPal as the payment method."""
        try:
            paypal_radio = self.browser.find_element(*self.SELECTORS['PAYPAL_RADIO'])
            paypal_radio.click()

            if not paypal_radio.is_selected():
                raise RuntimeError('PayPal radio button was not successfully selected')

            complete_purchase = self.browser.find_element(*self.SELECTORS['COMPLETE_PURCHASE_BUTTON'])
            complete_purchase.click()

            self.wait_for_ajax()

        except NoSuchElementException as e:
            raise RuntimeError(f"Failed to select PayPal payment method: {str(e)}")

    def verify_paypal_payment_success(self) -> bool:
        """Verify if the PayPal payment was successful."""
        try:
            WebDriverWait(self.browser, 10).until(
                EC.visibility_of_element_located(self.SELECTORS['PAYMENT_SUCCESS'])
            )
            return True
        except TimeoutException:
            return False

    def get_error_message(self) -> str:
        """Get the current error message displayed on the page."""
        element = self.browser.find_element(*self.SELECTORS['ERROR_MESSAGE'])
        return element.text

    def can_abandon_checkout(self) -> bool:
        """Check if the checkout can be abandoned."""
        try:
            button = self.browser.find_element(*self.SELECTORS['ABANDON_CHECKOUT_BUTTON'])
            return button.is_displayed() and 'disabled' not in button.get_attribute('class')
        except NoSuchElementException:
            return False

    def is_checkout_form_locked(self) -> bool:
        """Check if the checkout form is locked."""
        form = self.browser.find_element(*self.SELECTORS['CHECKOUT_FORM'])
        return ('locked' in form.get_attribute('class') or
                form.get_attribute('data-locked') is not None)

    def _parse_price(self, price_text: str) -> float:
        """Parse price string to float value."""
        cleaned_price = re.sub(r'[^\d.]', '', price_text)
        return float(cleaned_price)

    def switch_to_stripe_frame(self, frame_title: str) -> None:
        """Switch to a specific Stripe iframe by its title."""
        WebDriverWait(self.browser, 10).until(
            EC.frame_to_be_available_and_switch_to_it(
                (By.CSS_SELECTOR, f'iframe[title="{frame_title}"]')
            )
        )
