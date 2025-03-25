from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from features.pages.Common.base_page import BasePage
import logging

logger = logging.getLogger(__name__)

class PayPalPage(BasePage):
    """Page object for the PayPal payment page."""

    SELECTORS = {
        'EMAIL_FIELD': (By.ID, 'email'),
        'PASSWORD_FIELD': (By.ID, 'password'),
        'NEXT_BUTTON': (By.CSS_SELECTOR, 'button[data-testid="next-button"]'),
        'LOGIN_BUTTON': (By.CSS_SELECTOR, 'button[data-testid="login-button"]'),
        'AMOUNT': (By.CSS_SELECTOR, '.test_transaction-amount'),
        'CONFIRM_BUTTON': (By.ID, 'confirmButtonTop'),
        'PAYPAL_PAYMENT_OPTION': (By.ID, 'paypal-payment-option'),
        'PAYPAL_BUTTON': (By.ID, 'paypal-button'),
        'ERROR_MESSAGE': (By.CSS_SELECTOR, '.notification-critical'),
        'SUCCESS_MESSAGE': (By.CSS_SELECTOR, '.payment-success-message')
    }

    def __init__(self, browser):
        super().__init__(browser)
        self.url = '/paypal'

    def verify_page(self) -> None:
        """Verify that we're on the expected page."""
        try:
            self.wait_for_element_visible(self.SELECTORS['EMAIL_FIELD'])
        except TimeoutException as e:
            error_msg = f"Failed to verify PayPal page: {str(e)}"
            logger.error(error_msg)
            raise TimeoutException(error_msg)

    def login(self, username: str, password: str) -> None:
        """
        Login to PayPal with provided credentials.

        :param username: PayPal username/email
        :param password: PayPal password
        :raises RuntimeError: If login process fails
        """
        try:
            logger.info(f"Attempting to login with username: {username}")

            # Enter email and click next
            self.wait_for_element_visible(self.SELECTORS['EMAIL_FIELD'])
            email_field = self.browser.find_element(*self.SELECTORS['EMAIL_FIELD'])
            email_field.clear()
            email_field.send_keys(username)
            self.browser.find_element(*self.SELECTORS['NEXT_BUTTON']).click()

            # Enter password and click login
            self.wait_for_element_visible(self.SELECTORS['PASSWORD_FIELD'])
            password_field = self.browser.find_element(*self.SELECTORS['PASSWORD_FIELD'])
            password_field.clear()
            password_field.send_keys(password)
            self.browser.find_element(*self.SELECTORS['LOGIN_BUTTON']).click()

            logger.info("Login attempt completed")
        except Exception as e:
            error_msg = f"PayPal login failed: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def get_displayed_amount(self) -> str:
        """
        Get the displayed transaction amount.

        :return: The displayed amount
        :raises NoSuchElementException: If amount element is not found
        """
        try:
            element = self.browser.find_element(*self.SELECTORS['AMOUNT'])
            return element.text
        except NoSuchElementException as e:
            error_msg = f"Failed to get displayed amount: {str(e)}"
            logger.error(error_msg)
            raise NoSuchElementException(error_msg)

    def confirm_payment(self) -> None:
        """
        Confirm the PayPal payment.

        :raises RuntimeError: If confirmation fails
        """
        try:
            logger.info("Attempting to confirm payment")
            self.wait_for_element_visible(self.SELECTORS['CONFIRM_BUTTON'])
            self.browser.find_element(*self.SELECTORS['CONFIRM_BUTTON']).click()
            logger.info("Payment confirmation completed")
        except Exception as e:
            error_msg = f"Failed to confirm PayPal payment: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def wait_for_redirect_to_paypal(self) -> None:
        """
        Wait for redirect to PayPal.

        :raises RuntimeError: If redirect timeout occurs
        """
        try:
            logger.info("Waiting for redirect to PayPal")
            WebDriverWait(self.browser, 10).until(
                lambda driver: 'sandbox.paypal.com' in driver.current_url
            )
            logger.info("Successfully redirected to PayPal")
        except TimeoutException as e:
            error_msg = f"Failed to redirect to PayPal: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def has_login_error(self) -> bool:
        """
        Check if there's a login error.

        :return: True if login error is present
        """
        try:
            self.wait_for_element_visible(self.SELECTORS['ERROR_MESSAGE'])
            error_element = self.browser.find_element(*self.SELECTORS['ERROR_MESSAGE'])
            has_error = 'Some of your info is not correct' in error_element.text
            logger.info(f"Login error status: {has_error}")
            return has_error
        except (TimeoutException, NoSuchElementException):
            logger.info("No login error found")
            return False

    def wait_for_url_contains(self, url: str) -> None:
        """
        Wait for URL to contain specific string.

        :param url: URL substring to wait for
        """
        WebDriverWait(self.browser, 10).until(
            lambda driver: url in driver.current_url
        )

    def select_paypal_payment(self) -> None:
        """
        Select PayPal as payment method.

        :raises RuntimeError: If selection fails
        """
        try:
            logger.info("Attempting to select PayPal payment")
            self.wait_for_element_visible(self.SELECTORS['PAYPAL_PAYMENT_OPTION'])
            self.browser.find_element(*self.SELECTORS['PAYPAL_PAYMENT_OPTION']).click()

            self.wait_for_element_visible(self.SELECTORS['PAYPAL_BUTTON'])
            self.browser.find_element(*self.SELECTORS['PAYPAL_BUTTON']).click()

            logger.info("Successfully selected PayPal payment")
        except Exception as e:
            error_msg = f"Failed to select PayPal payment: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def is_payment_successful(self) -> bool:
        """
        Check if payment was successful.

        :return: True if payment was successful
        """
        try:
            self.wait_for_element_visible(self.SELECTORS['SUCCESS_MESSAGE'])
            logger.info("Payment successful")
            return True
        except TimeoutException:
            logger.info("Payment not successful")
            return False

    def wait_for_element_visible(self, selector: tuple, timeout: int = 10) -> None:
        """
        Wait for element to be visible on the page.

        :param selector: Tuple containing By and selector string
        :param timeout: Maximum time to wait in seconds
        :raises TimeoutException: If element is not visible within timeout
        """
        WebDriverWait(self.browser, timeout).until(
            EC.visibility_of_element_located(selector)
        )
